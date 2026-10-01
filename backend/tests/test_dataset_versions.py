import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://wheatbi:wheatbi_dev_password@127.0.0.1:5432/wheatbi",
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import SessionLocal
from models import (
    Dataset,
    DatasetStatus,
    DatasetType,
    DatasetVersion,
    DatasetVersionStatus,
    Project,
)


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


def create_project(db, name_prefix: str = "TEMP_PROJECT") -> Project:
    project = Project(name=f"{name_prefix}_{uuid4().hex[:8]}")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_dataset(db, project_id, name_prefix: str = "TEMP_DATASET") -> Dataset:
    dataset = Dataset(
        project_id=project_id,
        name=f"{name_prefix}_{uuid4().hex[:8]}",
        description="Temporary dataset for DatasetVersion ORM verification",
        dataset_type=DatasetType.GENOMIC,
        status=DatasetStatus.REGISTERED,
        source="pytest",
        format="CSV",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def create_dataset_version(
    db,
    dataset_id,
    version_number: int,
    description: str = "Temporary dataset version",
):
    version = DatasetVersion(
        dataset_id=dataset_id,
        version_number=version_number,
        description=description,
        file_name=f"dataset_v{version_number}.csv",
        file_format="CSV",
        file_size_bytes=1024,
        checksum_sha256="a" * 64,
        row_count=10,
        column_count=3,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def test_dataset_version_creation():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_CREATION")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_CREATION")
        try:
            version = create_dataset_version(db, dataset.id, 1, "Initial creation check")
            assert version.id is not None
            assert version.dataset_id == dataset.id
            assert version.version_number == 1
        finally:
            cleanup_project(project.id)


def test_dataset_version_default_status_registered():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_DEFAULT_STATUS")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_DEFAULT_STATUS")
        try:
            version = create_dataset_version(db, dataset.id, 1, "Default status check")
            assert version.status == DatasetVersionStatus.REGISTERED
        finally:
            cleanup_project(project.id)


def test_dataset_version_retrieval_by_id():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_RETRIEVAL")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_RETRIEVAL")
        try:
            created = create_dataset_version(db, dataset.id, 7, "Retrieval check")
            retrieved = db.get(DatasetVersion, created.id)

            assert retrieved is not None
            assert retrieved.id == created.id
            assert retrieved.dataset_id == dataset.id
            assert retrieved.version_number == 7
            assert retrieved.file_name == "dataset_v7.csv"
            assert retrieved.status == DatasetVersionStatus.REGISTERED
        finally:
            cleanup_project(project.id)


def test_dataset_version_parent_relationship():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_PARENT")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_PARENT")
        try:
            version = create_dataset_version(db, dataset.id, 3, "Parent relationship check")
            assert version.dataset is not None
            assert version.dataset.id == dataset.id
            assert version.dataset.name == dataset.name
        finally:
            cleanup_project(project.id)


def test_dataset_versions_child_collection_includes_created_version():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_CHILD")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_CHILD")
        try:
            version = create_dataset_version(db, dataset.id, 4, "Child collection check")
            db.refresh(dataset)
            assert dataset.versions is not None
            assert any(item.id == version.id for item in dataset.versions)
        finally:
            cleanup_project(project.id)


def test_dataset_version_multiple_versions_for_same_dataset():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_MULTIPLE")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_MULTIPLE")
        try:
            first = create_dataset_version(db, dataset.id, 1, "First version")
            second = create_dataset_version(db, dataset.id, 2, "Second version")

            rows = db.scalars(
                select(DatasetVersion).where(DatasetVersion.dataset_id == dataset.id)
            ).all()
            assert len(rows) == 2
            version_numbers = {row.version_number for row in rows}
            assert version_numbers == {1, 2}
            assert {row.id for row in rows} == {first.id, second.id}
        finally:
            cleanup_project(project.id)


def test_dataset_version_composite_uniqueness_on_dataset_and_version_number():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_UNIQUE")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_UNIQUE")
        try:
            first = create_dataset_version(db, dataset.id, 99, "Original unique version")
            with SessionLocal() as db2:
                duplicate = DatasetVersion(
                    dataset_id=dataset.id,
                    version_number=99,
                    description="Duplicate version number",
                    file_name="duplicate.csv",
                    file_format="CSV",
                )
                db2.add(duplicate)
                with pytest.raises(IntegrityError):
                    db2.commit()
                db2.rollback()

            assert db.get(DatasetVersion, first.id) is not None
            assert db.get(DatasetVersion, first.id).version_number == 99
        finally:
            cleanup_project(project.id)


def test_dataset_version_same_version_number_allowed_across_different_datasets():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_CROSS_DATASET")
        dataset_a = create_dataset(db, project.id, "TEMP_DATASET_A")
        dataset_b = create_dataset(db, project.id, "TEMP_DATASET_B")
        try:
            first = create_dataset_version(db, dataset_a.id, 1, "Dataset A version 1")
            second = create_dataset_version(db, dataset_b.id, 1, "Dataset B version 1")

            assert first.dataset_id != second.dataset_id
            assert first.version_number == second.version_number == 1
            assert first.dataset_id == dataset_a.id
            assert second.dataset_id == dataset_b.id
        finally:
            cleanup_project(project.id)


def test_dataset_version_rejects_nonexistent_dataset_foreign_key():
    with SessionLocal() as db:
        missing_dataset_id = uuid4()
        version = DatasetVersion(
            dataset_id=missing_dataset_id,
            version_number=1,
            description="Missing dataset reference",
            file_name="missing.csv",
            file_format="CSV",
        )
        db.add(version)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


def test_dataset_version_cleanup_and_isolation():
    with SessionLocal() as db:
        project = create_project(db, "TEMP_PROJECT_CLEANUP")
        dataset = create_dataset(db, project.id, "TEMP_DATASET_CLEANUP")
        try:
            version = create_dataset_version(db, dataset.id, 10, "Cleanup verification")
            assert version.id is not None

            db.delete(version)
            db.commit()

            remaining = db.get(DatasetVersion, version.id)
            assert remaining is None

            db.delete(dataset)
            db.delete(project)
            db.commit()

            assert db.get(Dataset, dataset.id) is None
            assert db.get(Project, project.id) is None
        finally:
            cleanup_project(project.id)
