import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://wheatbi:wheatbi_dev_password@127.0.0.1:5432/wheatbi",
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import SessionLocal
from main import app
from models import Dataset, DatasetStatus, DatasetType, DatasetVersion, DatasetVersionStatus, Project


@pytest.fixture(autouse=True)
def isolate_database_overrides():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


client = TestClient(app)


def cleanup_project(project_id):
    with SessionLocal() as db:
        dataset_rows = db.scalars(
            select(Dataset).where(Dataset.project_id == project_id)
        ).all()
        for dataset in dataset_rows:
            version_rows = db.scalars(
                select(DatasetVersion).where(DatasetVersion.dataset_id == dataset.id)
            ).all()
            for version in version_rows:
                db.delete(version)
            db.delete(dataset)

        project = db.get(Project, project_id)
        if project is not None:
            db.delete(project)

        db.commit()


def create_project_dataset(db, project_name: str = "TEMP_PROJECT", dataset_name: str = "TEMP_DATASET"):
    project = Project(name=f"{project_name}_{uuid4().hex[:8]}")
    db.add(project)
    db.commit()
    db.refresh(project)

    dataset = Dataset(
        project_id=project.id,
        name=f"{dataset_name}_{uuid4().hex[:8]}",
        description="Temporary dataset for DatasetVersion API verification",
        dataset_type=DatasetType.GENOMIC,
        status=DatasetStatus.REGISTERED,
        source="pytest",
        format="CSV",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return project, dataset


def test_create_dataset_version_successfully():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_CREATE", "TEMP_DATASET_CREATE")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "description": "Initial version",
                    "file_name": "initial.csv",
                    "file_format": "CSV",
                    "file_size_bytes": 2048,
                    "checksum_sha256": "a" * 64,
                    "row_count": 100,
                    "column_count": 5,
                },
            )

            assert response.status_code == 201, response.text
            payload = response.json()
            assert payload["dataset_id"] == str(dataset.id)
            assert payload["version_number"] == 1
            assert payload["status"] == "REGISTERED"
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_default_status_registered():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_DEFAULT", "TEMP_DATASET_DEFAULT")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 2,
                    "description": "Default status",
                    "file_name": "default.csv",
                    "file_format": "CSV",
                },
            )

            assert response.status_code == 201, response.text
            assert response.json()["status"] == DatasetVersionStatus.REGISTERED.value
        finally:
            cleanup_project(project.id)


def test_retrieve_dataset_version():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_RETRIEVE", "TEMP_DATASET_RETRIEVE")
        try:
            created = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 3,
                    "description": "Retrieve version",
                    "file_name": "retrieve.csv",
                    "file_format": "CSV",
                    "file_size_bytes": 1024,
                    "checksum_sha256": "b" * 64,
                    "row_count": 20,
                    "column_count": 2,
                },
            )
            assert created.status_code == 201, created.text
            version_id = created.json()["id"]

            response = client.get(f"/dataset-versions/{version_id}")
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["id"] == version_id
            assert payload["version_number"] == 3
            assert payload["dataset_id"] == str(dataset.id)
        finally:
            cleanup_project(project.id)


def test_list_dataset_versions_for_dataset():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_LIST", "TEMP_DATASET_LIST")
        try:
            first = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "v1.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "c" * 64,
                },
            )
            second = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 2,
                    "file_name": "v2.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "d" * 64,
                },
            )

            assert first.status_code == 201, first.text
            assert second.status_code == 201, second.text

            response = client.get(f"/datasets/{dataset.id}/versions/")
            assert response.status_code == 200, response.text
            payload = response.json()
            version_numbers = [item["version_number"] for item in payload]
            assert version_numbers == [1, 2]
        finally:
            cleanup_project(project.id)


def test_list_dataset_versions_orders_by_version_number_ascending():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_ORDER", "TEMP_DATASET_ORDER")
        try:
            for version_number in [3, 1, 2]:
                response = client.post(
                    "/dataset-versions/",
                    json={
                        "dataset_id": str(dataset.id),
                        "version_number": version_number,
                        "file_name": f"v{version_number}.csv",
                        "file_format": "CSV",
                        "checksum_sha256": ("e" * 64),
                    },
                )
                assert response.status_code == 201, response.text

            response = client.get(f"/datasets/{dataset.id}/versions/")
            assert response.status_code == 200, response.text
            payload = response.json()
            assert [item["version_number"] for item in payload] == [1, 2, 3]
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_nonexistent_dataset_returns_404():
    response = client.post(
        "/dataset-versions/",
        json={
            "dataset_id": str(uuid4()),
            "version_number": 1,
            "file_name": "missing.csv",
            "file_format": "CSV",
            "checksum_sha256": "f" * 64,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"


def test_list_dataset_versions_nonexistent_dataset_returns_404():
    response = client.get(f"/datasets/{uuid4()}/versions/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"


def test_get_nonexistent_dataset_version_returns_404():
    response = client.get(f"/dataset-versions/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "DatasetVersion not found"


def test_create_dataset_version_duplicate_version_number_returns_409():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_DUP", "TEMP_DATASET_DUP")
        try:
            first = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 10,
                    "file_name": "dup.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "1" * 64,
                },
            )
            assert first.status_code == 201, first.text

            second = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 10,
                    "file_name": "dup-2.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "2" * 64,
                },
            )

            assert second.status_code == 409, second.text
            assert second.json()["detail"] == "DatasetVersion for this dataset and version number already exists"
        finally:
            cleanup_project(project.id)


def test_same_version_number_can_exist_under_different_datasets():
    with SessionLocal() as db:
        project_a, dataset_a = create_project_dataset(db, "TEMP_PROJECT_A", "TEMP_DATASET_A")
        project_b, dataset_b = create_project_dataset(db, "TEMP_PROJECT_B", "TEMP_DATASET_B")
        try:
            first = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset_a.id),
                    "version_number": 1,
                    "file_name": "dataset-a.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "3" * 64,
                },
            )
            second = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset_b.id),
                    "version_number": 1,
                    "file_name": "dataset-b.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "4" * 64,
                },
            )

            assert first.status_code == 201, first.text
            assert second.status_code == 201, second.text
            assert first.json()["version_number"] == second.json()["version_number"] == 1
            assert first.json()["dataset_id"] == str(dataset_a.id)
            assert second.json()["dataset_id"] == str(dataset_b.id)
        finally:
            cleanup_project(project_a.id)
            cleanup_project(project_b.id)


def test_create_dataset_version_negative_version_number_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_NEGATIVE_VERSION", "TEMP_DATASET_NEGATIVE_VERSION")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": -1,
                    "file_name": "negative.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "5" * 64,
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_zero_version_number_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_ZERO_VERSION", "TEMP_DATASET_ZERO_VERSION")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 0,
                    "file_name": "zero.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "6" * 64,
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_negative_file_size_bytes_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_NEGATIVE_SIZE", "TEMP_DATASET_NEGATIVE_SIZE")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "negative-size.csv",
                    "file_format": "CSV",
                    "file_size_bytes": -1,
                    "checksum_sha256": "7" * 64,
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_invalid_sha256_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_BAD_SHA", "TEMP_DATASET_BAD_SHA")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "invalid-sha.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "not-a-valid-sha",
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_invalid_status_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_BAD_STATUS", "TEMP_DATASET_BAD_STATUS")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "bad-status.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "8" * 64,
                    "status": "NOT_A_STATUS",
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_negative_row_count_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_NEGATIVE_ROWS", "TEMP_DATASET_NEGATIVE_ROWS")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "negative-rows.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "9" * 64,
                    "row_count": -1,
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_create_dataset_version_negative_column_count_rejected():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_NEGATIVE_COLUMNS", "TEMP_DATASET_NEGATIVE_COLUMNS")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 1,
                    "file_name": "negative-columns.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "0" * 64,
                    "column_count": -1,
                },
            )

            assert response.status_code == 422
        finally:
            cleanup_project(project.id)


def test_dataset_version_response_contains_expected_fields():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_RESPONSE", "TEMP_DATASET_RESPONSE")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 5,
                    "description": "response validation",
                    "file_name": "response.csv",
                    "file_format": "CSV",
                    "file_size_bytes": 4096,
                    "checksum_sha256": "A" * 64,
                    "row_count": 250,
                    "column_count": 12,
                    "status": "READY",
                },
            )

            assert response.status_code == 201, response.text
            payload = response.json()
            assert set(payload.keys()) == {
                "id",
                "dataset_id",
                "version_number",
                "description",
                "file_name",
                "file_format",
                "file_size_bytes",
                "checksum_sha256",
                "row_count",
                "column_count",
                "status",
                "created_at",
                "updated_at",
            }
            assert payload["status"] == "READY"
        finally:
            cleanup_project(project.id)


def test_dataset_version_api_cleanup_removes_temp_rows():
    with SessionLocal() as db:
        project, dataset = create_project_dataset(db, "TEMP_PROJECT_CLEANUP_API", "TEMP_DATASET_CLEANUP_API")
        try:
            response = client.post(
                "/dataset-versions/",
                json={
                    "dataset_id": str(dataset.id),
                    "version_number": 99,
                    "file_name": "cleanup.csv",
                    "file_format": "CSV",
                    "checksum_sha256": "B" * 64,
                },
            )
            assert response.status_code == 201, response.text

            version_id = response.json()["id"]
            with SessionLocal() as cleanup_db:
                version = cleanup_db.get(DatasetVersion, version_id)
                assert version is not None
                cleanup_db.delete(version)
                cleanup_db.commit()

            with SessionLocal() as verify_db:
                remaining = verify_db.get(DatasetVersion, version_id)
                assert remaining is None

            cleanup_project(project.id)
            with SessionLocal() as verify_db:
                assert verify_db.get(Project, project.id) is None
                assert verify_db.get(Dataset, dataset.id) is None
        finally:
            cleanup_project(project.id)
