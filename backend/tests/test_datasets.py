import os
from pathlib import Path
import sys
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import Base, get_db
from main import app
from models import Dataset, Project

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def create_project_via_api(name: str = "Test Project") -> str:
    response = client.post(
        "/projects/",
        json={"name": name, "description": "Test project for dataset API"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def cleanup_project(project_id: str) -> None:
    project_uuid = UUID(project_id)

    with TestingSessionLocal() as db:
        dataset_rows = db.scalars(
            select(Dataset).where(Dataset.project_id == project_uuid)
        ).all()
        for dataset in dataset_rows:
            db.delete(dataset)

        project = db.get(Project, project_uuid)
        if project is not None:
            db.delete(project)

        db.commit()


def test_create_dataset_with_valid_project():
    project_id = create_project_via_api("Dataset Project A")
    try:
        response = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Genomic panel",
                "description": "Primary genomic dataset",
                "dataset_type": "GENOMIC",
                "status": "READY",
                "source": "Breeding station",
                "format": "VCF",
            },
        )

        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["project_id"] == project_id
        assert payload["name"] == "Genomic panel"
        assert payload["dataset_type"] == "GENOMIC"
        assert payload["status"] == "READY"
    finally:
        cleanup_project(project_id)


def test_reject_dataset_with_nonexistent_project():
    response = client.post(
        "/datasets/",
        json={
            "project_id": str(uuid4()),
            "name": "Missing project dataset",
            "dataset_type": "PHENOTYPIC",
        },
    )

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_reject_invalid_dataset_type():
    project_id = create_project_via_api("Dataset Project B")
    try:
        response = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Bad type dataset",
                "dataset_type": "NOT_A_TYPE",
            },
        )

        assert response.status_code == 422
    finally:
        cleanup_project(project_id)


def test_reject_invalid_status():
    project_id = create_project_via_api("Dataset Project C")
    try:
        response = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Bad status dataset",
                "dataset_type": "EXPERIMENTAL",
                "status": "NOT_A_STATUS",
            },
        )

        assert response.status_code == 422
    finally:
        cleanup_project(project_id)


def test_list_datasets():
    project_id = create_project_via_api("Dataset Project D")
    try:
        first = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Alpha dataset",
                "dataset_type": "ENVIRONMENTAL",
            },
        )
        second = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Beta dataset",
                "dataset_type": "DERIVED",
            },
        )

        assert first.status_code == 201, first.text
        assert second.status_code == 201, second.text

        response = client.get("/datasets/")
        assert response.status_code == 200, response.text
        payload = response.json()
        names = [item["name"] for item in payload]
        assert "Beta dataset" in names
        assert "Alpha dataset" in names
    finally:
        cleanup_project(project_id)


def test_retrieve_dataset():
    project_id = create_project_via_api("Dataset Project E")
    try:
        created = client.post(
            "/datasets/",
            json={
                "project_id": project_id,
                "name": "Single retrieval dataset",
                "dataset_type": "GENOMIC",
            },
        )
        dataset_id = created.json()["id"]

        response = client.get(f"/datasets/{dataset_id}")
        assert response.status_code == 200, response.text
        assert response.json()["id"] == dataset_id
        assert response.json()["name"] == "Single retrieval dataset"
    finally:
        cleanup_project(project_id)


def test_retrieve_nonexistent_dataset_returns_404():
    response = client.get(f"/datasets/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"
