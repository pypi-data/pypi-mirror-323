from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator

from advanced_alchemy.config import AlembicAsyncConfig, AlembicSyncConfig, SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from leaguemanager.core import get_settings

from .db_config import db_args, uri

__all__ = [
    "sync_alembic_config",
    "sync_engine",
    "sync_session_factory",
    "sync_config",
    "async_alembic_config",
    "async_engine",
    "async_session_factory",
    "async_config",
    "get_session",
    "get_async_session",
]


settings = get_settings()

# Sync DB Setup

sync_alembic_config = AlembicSyncConfig(
    version_table_name="alembic_version",
    script_config=str(settings.MIGRATION_CONFIG / "alembic.ini"),
    script_location=str(settings.MIGRATION_PATH),
    template_path=settings.ALEMBIC_TEMPLATE_PATH,
)
sync_engine = create_engine(url=uri(), **db_args)
sync_session_factory = sessionmaker(bind=sync_engine, expire_on_commit=False)
sync_config = SQLAlchemySyncConfig(
    engine_instance=sync_engine, session_maker=sync_session_factory, alembic_config=sync_alembic_config
)


@contextmanager
def get_session() -> Generator[Session, Any, None]:
    with sync_session_factory() as session:
        yield session


# Async DB Setup

async_alembic_config = AlembicAsyncConfig(
    version_table_name="alembic_version",
    script_config=str(settings.MIGRATION_CONFIG / "alembic.ini"),
    script_location=str(settings.MIGRATION_PATH),
)
async_engine = create_async_engine(url=uri(is_async=True), **db_args)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
async_config = SQLAlchemyAsyncConfig(
    create_engine_callable=create_async_engine,
    engine_instance=async_engine,
    session_maker=async_session_factory,
    alembic_config=async_alembic_config,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
