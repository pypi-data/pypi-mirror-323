from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator

from attrs import define, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from svcs import Container, Registry

from leaguemanager.core import get_settings
from leaguemanager.core.toolbox import get_advanced_alchemy_config, get_repositories, get_services
from leaguemanager.db import async_config, get_async_session, get_session, sync_config
from leaguemanager.dependency.managers import RepositoryManagement, ServiceManagement
from leaguemanager.services._typing import (
    AsyncRepositoryT,
    AsyncServiceT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncRepositoryT,
    SyncServiceT,
)

__all__ = ["LeagueManager"]

settings = get_settings()


@define
class LeagueManager:
    """Registry for managing services.

    TODO: Serve up async repos/services

    If no `Registry` is provided, this class creates one. Keep in mind that there should only
    be one registry per application. Database session is kept in a `Container` and is provided
    as needed. The same is true for all League Manager "services", which consist of database
    operations on those specific database tables (corresponding to its model).

    Attributes:
        service_registry (Registry | None): An `svcs` Registry for managing services.
        get_session (Generator[Session, Any, None]): A generator for a database session.
        get_async_session (AsyncGenerator[AsyncSession, Any]): A generator for an async database session.
        manager_sync_repos (list[type[SyncRepositoryT]]): List of repositories for sync database operations.
        manager_async_repos (list[type[AsyncRepositoryT]]): List of repositories for async database operations.
        manager_sync_services (list[type[SyncServiceT]]): List of services for sync database operations.
        manager_async_services (list[type[AsyncServiceT]]): List of services for async database operations.
        advanced_alchemy_sync_config (list[type[SQLAlchemySyncConfigT]]): List of Advanced Alchemy sync configurations.
        advanced_alchemy_async_config (list[type[SQLAlchemyAsyncConfigT]]): List of Advanced Alchemy async configurations.

    Example:
        >>> registry = LeagueManager()
        >>> season_service = registry.provide_db_service(SeasonSyncService)
        >>> team_service = registry.provide_db_service(TeamSyncService)
        >>>
        >>> season_service.list()  #  List all seasons
        >>> team_service.count()  #  Count number of teams

    """

    service_registry: Registry | None = field(default=None)

    get_session: Generator[Session, Any, None] = field(default=get_session)
    get_async_session: AsyncGenerator[AsyncSession, Any] = field(default=get_async_session)

    manager_sync_repos: list[type[SyncRepositoryT]] = field()
    manager_async_repos: list[type[AsyncRepositoryT]] = field()
    manager_sync_services: list[type[SyncServiceT]] = field()
    manager_async_services: list[type[AsyncServiceT]] = field()

    aa_config_dir: str = field(default=settings.ADVANCED_ALCHEMY_CONFIG_DIRNAME)

    advanced_alchemy_sync_config: list[type[SQLAlchemySyncConfigT]] = field(init=False)
    advanced_alchemy_async_config: list[type[SQLAlchemyAsyncConfigT]] = field(init=False)

    # Useful for integrating with other apps/frameworks
    _SVCS_KEY_REGISTRY: str = field(default="league_manager_registry")
    _SVCS_KEY_CONTAINER: str = field(default="league_manager")

    @manager_sync_repos.default
    def _dynamic_sync_repos(self) -> list[type[SyncRepositoryT]]:
        return get_repositories()

    @manager_async_repos.default
    def _dynamic_async_repos(self) -> list[type[AsyncRepositoryT]]:
        return get_repositories(is_async=True)

    @manager_sync_services.default
    def _dynamic_sync_services(self) -> list[type[SyncServiceT]]:
        return get_services()

    @manager_async_services.default
    def _dynamic_async_services(self) -> list[type[AsyncServiceT]]:
        return get_services(is_async=True)

    def __attrs_post_init__(self):
        # check existing project has a python module not in venv or tests
        if not self.aa_config_dir:
            raise ValueError(
                "Cannot find a python module. Please create a .py file in the root or subdirectory of your project."
            )

        if not self.service_registry:
            self.service_registry = Registry()

        # Register Advanced Alchemy objects

        for repo_type in self.manager_sync_repos:
            self.register_db_repository(repository_type=repo_type)
        for service_type in self.manager_sync_services:
            self.register_db_service(service_type=service_type)

        if _dirname := self.aa_config_dir:
            _sync_config = get_advanced_alchemy_config(_dirname)
            _async_config = get_advanced_alchemy_config(_dirname, is_async=True)
        if not _sync_config:
            _sync_config = [sync_config]
        if not _async_config:
            _async_config = [async_config]
        for _config in _sync_config:
            self.registry.register_value(SQLAlchemySyncConfigT, _config)
        for _config in _async_config:
            self.registry.register_value(SQLAlchemyAsyncConfigT, _config)

    @property
    def registry(self) -> Registry:
        return self.service_registry

    # Register additional objects

    @contextmanager
    def sync_session_container(self) -> Generator[Container, None, None]:
        """Create a container for a sync database session."""
        self.registry.register_factory(Session, self.get_session)
        with Container(self.registry) as container:
            yield container

    @asynccontextmanager
    async def async_session_container(self) -> AsyncGenerator[Container, None]:
        """Create a container for an async database session."""
        self.registry.register_factory(AsyncSession, self.get_async_session)
        async with Container(self.registry) as container:
            yield container

    def register_db_repository(self, repository_type: type[SyncRepositoryT]) -> None:
        """Register a League Manager repository based on its type."""
        _repository = RepositoryManagement(repository_type=repository_type, db_session=self.provide_db_session)
        self.registry.register_value(repository_type, _repository.get_repository)

    def register_db_service(self, service_type: type[SyncServiceT]) -> None:
        """Register a League Manager service based on its type."""
        _service = ServiceManagement(service_type=service_type, db_session=self.provide_db_session)
        self.registry.register_value(service_type, next(_service.get_service))

    # # Retrieve objects

    @property
    def provide_db_session(self) -> Session:
        """Provide a sync database session."""
        with self.sync_session_container() as container:
            return container.get(Session)

    @property
    def provide_async_db_session(self) -> AsyncSession:
        """Provide an async database session."""
        with self.async_session_container() as container:
            return container.get(AsyncSession)

    @property
    def provide_sync_config(self) -> SQLAlchemySyncConfigT:
        return Container(self.registry).get(SQLAlchemySyncConfigT)

    @property
    def provide_async_config(self) -> SQLAlchemyAsyncConfigT:
        return Container(self.registry).get(SQLAlchemyAsyncConfigT)

    def provide_db_repository(self, repository_type: type[SyncRepositoryT]) -> type[SyncRepositoryT]:
        """Provide a League Manager repository based on its type."""
        return Container(self.registry).get(repository_type)

    def provide_db_service(self, service_type: type[SyncServiceT]) -> type[SyncServiceT]:
        """Provide a League Manager service based on its type."""
        return Container(self.registry).get(service_type)
