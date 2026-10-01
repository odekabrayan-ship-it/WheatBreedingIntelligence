import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Dataset, DatasetVersion, DatasetVersionStatus


router = APIRouter(
    tags=["Dataset Versions"],
)


class DatasetVersionCreate(BaseModel):
    dataset_id: UUID
    version_number: int = Field(..., gt=0)
    description: str | None = None
    file_name: str | None = Field(default=None, max_length=255)
    file_format: str | None = Field(default=None, max_length=50)
    file_size_bytes: int | None = Field(default=None, ge=0)
    checksum_sha256: str | None = None
    row_count: int | None = Field(default=None, ge=0)
    column_count: int | None = Field(default=None, ge=0)
    status: DatasetVersionStatus | None = None

    @field_validator("checksum_sha256")
    @classmethod
    def validate_checksum_sha256(cls, value: str | None) -> str | None:
        if value is None:
            return value

        if not re.fullmatch(r"[0-9a-fA-F]{64}", value):
            raise ValueError("checksum_sha256 must be a valid SHA-256 hex digest")

        return value


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dataset_id: UUID
    version_number: int
    description: str | None
    file_name: str | None
    file_format: str | None
    file_size_bytes: int | None
    checksum_sha256: str | None
    row_count: int | None
    column_count: int | None
    status: DatasetVersionStatus
    created_at: str
    updated_at: str


def serialize_dataset_version(version: DatasetVersion) -> DatasetVersionResponse:
    return DatasetVersionResponse(
        id=version.id,
        dataset_id=version.dataset_id,
        version_number=version.version_number,
        description=version.description,
        file_name=version.file_name,
        file_format=version.file_format,
        file_size_bytes=version.file_size_bytes,
        checksum_sha256=version.checksum_sha256,
        row_count=version.row_count,
        column_count=version.column_count,
        status=version.status,
        created_at=version.created_at.isoformat(),
        updated_at=version.updated_at.isoformat(),
    )


@router.post("/dataset-versions/", response_model=DatasetVersionResponse, status_code=201)
def create_dataset_version(
    dataset_version_data: DatasetVersionCreate,
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, dataset_version_data.dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    version = DatasetVersion(
        dataset_id=dataset_version_data.dataset_id,
        version_number=dataset_version_data.version_number,
        description=dataset_version_data.description,
        file_name=dataset_version_data.file_name,
        file_format=dataset_version_data.file_format,
        file_size_bytes=dataset_version_data.file_size_bytes,
        checksum_sha256=dataset_version_data.checksum_sha256,
        row_count=dataset_version_data.row_count,
        column_count=dataset_version_data.column_count,
        status=dataset_version_data.status or DatasetVersionStatus.REGISTERED,
    )

    db.add(version)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="DatasetVersion for this dataset and version number already exists",
        ) from exc

    db.refresh(version)
    return serialize_dataset_version(version)


@router.get("/datasets/{dataset_id}/versions/", response_model=list[DatasetVersionResponse])
def list_dataset_versions_for_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    versions = db.scalars(
        select(DatasetVersion)
        .where(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.version_number.asc())
    ).all()

    return [serialize_dataset_version(version) for version in versions]


@router.get("/dataset-versions/{dataset_version_id}", response_model=DatasetVersionResponse)
def get_dataset_version(
    dataset_version_id: UUID,
    db: Session = Depends(get_db),
):
    version = db.get(DatasetVersion, dataset_version_id)
    if version is None:
        raise HTTPException(
            status_code=404,
            detail="DatasetVersion not found",
        )

    return serialize_dataset_version(version)
