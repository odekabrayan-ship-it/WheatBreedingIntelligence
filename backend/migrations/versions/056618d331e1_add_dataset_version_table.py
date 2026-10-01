"""add_dataset_version_table

Revision ID: 056618d331e1
Revises: 6d5ca322a758
Create Date: 2026-10-01 14:49:37.909668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '056618d331e1'
down_revision: Union[str, Sequence[str], None] = '6d5ca322a758'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE dataset_version_status AS ENUM ('REGISTERED', 'PROCESSING', 'READY', 'FAILED', 'ARCHIVED')"
    )

    op.create_table(
        "dataset_versions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "dataset_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_format", sa.String(length=50), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("column_count", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "REGISTERED",
                "PROCESSING",
                "READY",
                "FAILED",
                "ARCHIVED",
                name="dataset_version_status",
                create_type=False,
            ),
            nullable=False,
            server_default="REGISTERED",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index(
        op.f("ix_dataset_versions_dataset_id"),
        "dataset_versions",
        ["dataset_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_dataset_versions_dataset_version_number",
        "dataset_versions",
        ["dataset_id", "version_number"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_dataset_versions_dataset_version_number",
        "dataset_versions",
        type_="unique",
    )
    op.drop_index(op.f("ix_dataset_versions_dataset_id"), table_name="dataset_versions")
    op.drop_table("dataset_versions")
    op.execute("DROP TYPE IF EXISTS dataset_version_status")
