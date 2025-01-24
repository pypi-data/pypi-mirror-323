import inspect
from datetime import datetime
from importlib import import_module
from inspect import isclass, signature
from pathlib import Path
from typing import Any, Iterable, Iterator

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager.core import get_settings
from leaguemanager.models.base import UUIDBase

settings = get_settings()


def get_modules(module: str) -> Iterator[str]:
    """Returns all .py modules in given file_dir.

    Args:
        module (str): Name of directory to begin recursive search

    Yields:
        Iterator[str]: The generator contains paths to modules
        with dot notation starting at project root.
        (For example: "app.models.user")

    References:
        [Bob Waycott](
            https://bobwaycott.com/blog/how-i-use-flask/organizing-flask-models-with-automatic-discovery/
            )
    """
    app_root = Path(settings.MODULE_DIR)
    if app_root.name == module:
        file_dir = app_root
    else:
        file_dir = app_root / module
    idx_app_root = len(app_root.parts) - 1  # index of app root
    modules = [f for f in list(file_dir.rglob("*.py")) if not f.stem == "__init__"]
    for filepath in modules:
        yield (".".join(filepath.parts[idx_app_root:])[0:-3])


def dynamic_loader(module: str, compare: bool) -> Iterable:
    """Iterates over all .py files in `module` directory, finding all classes that
    match `compare` function.

    Other classes/objects in the module directory will be ignored. Note that only objects
    contained within the `__all__` attribute will be loaded.

    Returns unique items found.

    Args:
        module (str): Directory name to search recursively
        compare (function): Boolean comparison of all py files in
        `module` directory

    Returns:
        list: All modules that match the `compare` function.

    References:
        [Bob Waycott](
            https://bobwaycott.com/blog/how-i-use-flask/organizing-flask-models-with-automatic-discovery/
            )
    """
    items = []
    for mod in get_modules(module):
        try:
            _module = import_module(mod)
        except AttributeError:
            # Ignore modules that create circular imports
            continue
        if hasattr(_module, "__all__"):
            objs = [getattr(_module, obj) for obj in _module.__all__]
            items += [o for o in objs if compare(o) and o not in items]

    return items


def get_signature(func):
    """Returns signature of given function"""
    if hasattr(func, "__wrapped__"):
        return signature(func.__wrapped__)
    return signature(func)


def is_sync_repo(item: Any):
    """Checks if item is SQLAlchemySyncRepository class or subclass"""
    return isclass(item) and issubclass(item, SQLAlchemySyncRepository)


def is_async_repo(item: Any):
    """Checks if item is SQLAlchemyAsyncRepository class or subclass"""
    return isclass(item) and issubclass(item, SQLAlchemyAsyncRepository)


def is_sync_service(item: Any):
    """Checks if item is SQLAlchemySyncRepositoryService class or subclass."""
    return isclass(item) and issubclass(item, SQLAlchemySyncRepositoryService)


def is_async_service(item: Any):
    """Checks if item is SQLAlchemyAsyncRepositoryService class or subclass."""
    return isclass(item) and issubclass(item, SQLAlchemyAsyncRepositoryService)


def is_sync_config(item: Any):
    """Checks if item is a SQLAlchemySyncConfig.

    Was unable to use `issubclass` here. May need to look into it more at some point.
    """
    return item.__class__ == SQLAlchemySyncConfig


def is_async_config(item: Any):
    """Checks if item is a SQLAlchemyAsyncConfig.

    Was unable to use `issubclass` here. May need to look into it more at some point.
    """
    return item.__class__ == SQLAlchemyAsyncConfig


def get_services(is_async: bool = False) -> list[SQLAlchemySyncRepositoryService | SQLAlchemyAsyncRepositoryService]:
    """Returns all SQLAlchemySyncRepositoryService or SQLAlchemyAsyncRepositoryService classes dynamically.

    Args:
        is_async (bool, optional): If True, returns all SQLAlchemyAsyncRepositoryService classes.
        Defaults to False.
    """
    if is_async:
        return dynamic_loader("services", is_async_service)
    return dynamic_loader("services", is_sync_service)


def get_repositories(is_async: bool = False) -> list[SQLAlchemyAsyncRepository | SQLAlchemySyncRepository]:
    """Returns all SQLAlchemySyncRepository or SQLAlchemyAsyncRepository classes dynamically.

    Args:
        is_async (bool, optional): If True, returns all SQLAlchemyAsyncRepository classes.
        Defaults to False.

    Returns:
        list: List of SQLAlchemySyncRepository or SQLAlchemyAsyncRepository classes
    """
    if is_async:
        return dynamic_loader("repository", is_async_repo)
    return dynamic_loader("repository", is_sync_repo)


def get_advanced_alchemy_config(module_name: str = "app", is_async: bool = False):
    """Returns Advanced Alchemy config classes, including SQLAlchemySyncConfig and SQLAlchemyAsyncConfig.

    This function will find any `SQLAlchemySyncConfig` or `SQLAlchemyAsyncConfig` classes (or subclasses) contained
    within the `module_name` directory. It will search recursively and return all classes found. However, the
    module must be included in the `__all__` list of wherever it is imported. For example:

    Example:
        >>> from advanced_alchemy.config import SQLAlchemySyncConfig
        >>>
        >>> __all__ = ["sync_config"]
        >>>
        >>> sync_config = SQLAlchemySyncConfig(...)

    If the `module_name` is `db_config`, then it will search the `db_config` directory and all subdirectories for
    a matching `SQLAlchemySyncConfig` or `SQLAlchemyAsyncConfig` class.

    If no `module_name` is provided, it will default to "app", and search there recursively.

    If none are found, it will return an empty list.

    Args:
        module_name (str, optional): The name of the module to search within. Defaults to "app".
        is_async (bool, optional): If True, returns all SQLAlchemyAsyncConfig classes. Defaults to False.

    Returns:
        list: A list of SQLAlchemySyncConfig or SQLAlchemyAsyncConfig classes.
    """
    if is_async:
        return dynamic_loader(module_name, is_async_config)
    return dynamic_loader(module_name, is_sync_config)


def clear_table(session: Session, model: UUIDBase) -> None:
    """Clears table of given model."""
    session.execute(delete(model))


def str_to_iso(date_string: str, format: str):
    """Converts string to datetime object."""
    return datetime.strptime(date_string, format)
