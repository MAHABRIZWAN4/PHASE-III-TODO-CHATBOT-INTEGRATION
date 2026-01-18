"""Alembic migration environment configuration.

This module configures Alembic to work with SQLModel and async PostgreSQL.
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Import all models to ensure they're registered with SQLModel metadata
from models import User, Task  # Existing models
from app.models import Conversation, Message  # New chat models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = SQLModel.metadata

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Convert to async URL for migrations
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Strip libpq params that break asyncpg
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?sslmode=require&channel_binding=require", "")
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("&sslmode=require&channel_binding=require", "")
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?sslmode=require", "")
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("&sslmode=require", "")
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?channel_binding=require", "")
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("&channel_binding=require", "")
    config.set_main_option("sqlalchemy.url", ASYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
