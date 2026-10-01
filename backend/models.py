from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class DatasetType(str, Enum):
    GENOMIC = "GENOMIC"
    PHENOTYPIC = "PHENOTYPIC"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    EXPERIMENTAL = "EXPERIMENTAL"
    DERIVED = "DERIVED"


class DatasetStatus(str, Enum):
    REGISTERED = "REGISTERED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class DatasetVersionStatus(str, Enum):
    REGISTERED = "REGISTERED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="project",
    )


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    project_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dataset_type: Mapped[DatasetType] = mapped_column(
        SAEnum(DatasetType, name="dataset_type", create_type=True),
        nullable=False,
    )

    status: Mapped[DatasetStatus] = mapped_column(
        SAEnum(DatasetStatus, name="dataset_status", create_type=True),
        nullable=False,
        default=DatasetStatus.REGISTERED,
    )

    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project: Mapped[Project] = relationship(
        back_populates="datasets",
    )

    versions: Mapped[list["DatasetVersion"]] = relationship(
        back_populates="dataset",
    )


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    dataset_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    checksum_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    row_count: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    column_count: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[DatasetVersionStatus] = mapped_column(
        SAEnum(DatasetVersionStatus, name="dataset_version_status", create_type=True),
        nullable=False,
        default=DatasetVersionStatus.REGISTERED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    dataset: Mapped[Dataset] = relationship(
        back_populates="versions",
    )
