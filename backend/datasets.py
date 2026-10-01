from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Dataset, DatasetStatus, DatasetType, Project


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


class DatasetCreate(BaseModel):
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    dataset_type: DatasetType
    status: DatasetStatus = DatasetStatus.REGISTERED
    source: str | None = Field(default=None, max_length=500)
    format: str | None = Field(default=None, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Name cannot be empty")
        return cleaned_value


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    description: str | None
    dataset_type: DatasetType
    status: DatasetStatus
    source: str | None
    format: str | None
    created_at: str
    updated_at: str


@router.post("/", response_model=DatasetResponse, status_code=201)
def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
):
    project = db.get(Project, dataset_data.project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    dataset = Dataset(
        project_id=dataset_data.project_id,
        name=dataset_data.name,
        description=dataset_data.description,
        dataset_type=dataset_data.dataset_type,
        status=dataset_data.status,
        source=dataset_data.source,
        format=dataset_data.format,
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        project_id=dataset.project_id,
        name=dataset.name,
        description=dataset.description,
        dataset_type=dataset.dataset_type,
        status=dataset.status,
        source=dataset.source,
        format=dataset.format,
        created_at=dataset.created_at.isoformat(),
        updated_at=dataset.updated_at.isoformat(),
    )


@router.get("/", response_model=list[DatasetResponse])
def list_datasets(
    db: Session = Depends(get_db),
):
    datasets = db.scalars(
        select(Dataset).order_by(Dataset.created_at.desc())
    ).all()

    return [
        DatasetResponse(
            id=dataset.id,
            project_id=dataset.project_id,
            name=dataset.name,
            description=dataset.description,
            dataset_type=dataset.dataset_type,
            status=dataset.status,
            source=dataset.source,
            format=dataset.format,
            created_at=dataset.created_at.isoformat(),
            updated_at=dataset.updated_at.isoformat(),
        )
        for dataset in datasets
    ]


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return DatasetResponse(
        id=dataset.id,
        project_id=dataset.project_id,
        name=dataset.name,
        description=dataset.description,
        dataset_type=dataset.dataset_type,
        status=dataset.status,
        source=dataset.source,
        format=dataset.format,
        created_at=dataset.created_at.isoformat(),
        updated_at=dataset.updated_at.isoformat(),
    )
