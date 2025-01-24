from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Role
from leaguemanager.repository import RoleAsyncRepository, RoleSyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["RoleSyncService", "RoleAsyncService"]


class RoleSyncService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = RoleSyncRepository


class RoleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = RoleAsyncRepository
