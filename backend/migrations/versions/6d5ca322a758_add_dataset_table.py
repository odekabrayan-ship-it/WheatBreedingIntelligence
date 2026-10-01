"""add_dataset_table

Revision ID: 6d5ca322a758
Revises: b609a5015b26
Create Date: 2026-10-01 11:52:42.899822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d5ca322a758'
down_revision: Union[str, Sequence[str], None] = 'b609a5015b26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE dataset_type AS ENUM ('GENOMIC', 'PHENOTYPIC', 'ENVIRONMENTAL', 'EXPERIMENTAL', 'DERIVED')"
    )
    op.execute(
        "CREATE TYPE dataset_status AS ENUM ('REGISTERED', 'PROCESSING', 'READY', 'FAILED', 'ARCHIVED')"
    )

    op.create_table(
        "datasets",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "dataset_type",
            sa.Enum(
                "GENOMIC",
                "PHENOTYPIC",
                "ENVIRONMENTAL",
                "EXPERIMENTAL",
                "DERIVED",
                name="dataset_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "REGISTERED",
                "PROCESSING",
                "READY",
                "FAILED",
                "ARCHIVED",
                name="dataset_status",
                create_type=False,
            ),
            nullable=False,
            server_default="REGISTERED",
        ),
        sa.Column("source", sa.String(length=500), nullable=True),
        sa.Column("format", sa.String(length=50), nullable=True),
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
        op.f("ix_datasets_project_id"),
        "datasets",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_datasets_project_id"), table_name="datasets")
    op.drop_table("datasets")
    op.execute("DROP TYPE IF EXISTS dataset_status")
    op.execute("DROP TYPE IF EXISTS dataset_type")
