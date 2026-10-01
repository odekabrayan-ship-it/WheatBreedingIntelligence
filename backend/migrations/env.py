from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv
import os


# Add the backend directory to Python's import path.
BASE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = BASE_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# Load backend/.env
load_dotenv(BACKEND_DIR / ".env")


# Import SQLAlchemy metadata.
from models import Base


# Alembic Config object.
config = context.config


# Configure logging when an alembic.ini file is available.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used for autogeneration.
target_metadata = Base.metadata


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL was not found in backend/.env"
        )

    return database_url


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using an active database connection."""

    configuration = config.get_section(config.config_ini_section)

    if configuration is None:
        raise RuntimeError(
            "Alembic configuration section could not be loaded."
        )

    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()