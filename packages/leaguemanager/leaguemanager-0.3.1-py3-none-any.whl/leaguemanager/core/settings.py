import os
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from attrs import define, field


@define
class Settings:
    # League Manager app info
    DEFAULT_MODULE_NAME: str = "leaguemanager"
    MODULE_DIR: str = field()

    @MODULE_DIR.default
    def _default_base_dir(self):
        return self._module_to_os_path(self.DEFAULT_MODULE_NAME)

    # User Application directory -
    APP_DIR: Path = field(init=False)

    @APP_DIR.default
    def _default_app_dir(self):
        """Check environment variable for app directory first.

        If not found, return current working directory. This is primarily set if League Manager
        is going to be installed as a dependency.
        """
        try:
            _APP_DIR = os.getenv("APP_DIR")
            if not _APP_DIR:
                return Path.cwd()
            return Path(_APP_DIR)
        except ValueError:
            return Path.cwd()

    # Advanced Alchemy configuration
    ADVANCED_ALCHEMY_CONFIG_DIRNAME: str = field(init=False)

    # ALembic settings
    MIGRATION_PATH: Path = field(init=False)
    MIGRATION_CONFIG: str = field(init=False)
    ALEMBIC_TEMPLATE_PATH: str = field(init=False)

    # SQLite settings
    SQLITE_DATA_DIRECTORY: Path = field(init=False)
    DATE_FORMAT: str = field(default="%Y-%m-%d %H:%M:%S")

    @ADVANCED_ALCHEMY_CONFIG_DIRNAME.default
    def _default_advanced_alchemy_config_dirname(self):
        """Check for environment variable with name of directory containing Advanced Alchemy config object(s).

        If not found, recurse through current directory (ignoring certain directories) to find
        first directory with containing a `.py` file.
        """
        if aa_config_dir := os.getenv("ADVANCED_ALCHEMY_CONFIG_DIRNAME"):
            if not Path(aa_config_dir).is_dir():
                raise ValueError(f"Environment Variable refers to invalid directory: {aa_config_dir}")
            return aa_config_dir
        else:
            _exclude = ["venv", ".venv", "tests", "docs", "migrations"]
            for f in Path.cwd().rglob("**/*.py"):
                match f:
                    case f if any(x in f.parts for x in _exclude):
                        continue
                    case f if f.parent.name == "__pycache__":
                        continue
                    case _:
                        return f.parent.name

    @MIGRATION_PATH.default
    def _default_migration_path(self):
        """Check for environment variable first."""
        if "MIGRATION_PATH" in os.environ:
            migration_path = Path(os.getenv("MIGRATION_PATH"))
            return Path(self.APP_DIR / migration_path, exist_ok=True)
        else:
            return self.APP_DIR / "migrations"

    @MIGRATION_CONFIG.default
    def _default_migration_config(self):
        """If environment variable does not exist, set directory where alembic.ini will be stored."""
        if "MIGRATION_CONFIG" in os.environ:
            return Path(os.getenv("MIGRATION_CONFIG"))
        else:
            return self.APP_DIR

    @ALEMBIC_TEMPLATE_PATH.default
    def _default_alembic_template_path(self):
        """Internally used by League Manager to generate Alembic migration files.

        They are created with the `alembic init` command. However, if the environment variable
        `ALEMBIC_TEMPLATE_PATH` is set, we use that instead for custom Alembic template files."""
        if "ALEMBIC_TEMPLATE_PATH" in os.environ:
            return Path(os.getenv("ALEMBIC_TEMPLATE_PATH"))
        else:
            return Path(self.MODULE_DIR) / "db/alembic_templates"

    @SQLITE_DATA_DIRECTORY.default
    def _default_data_directory(self):
        if "SQLITE_DATA_DIRECTORY" in os.environ:
            return os.getenv("SQLITE_DATA_DIRECTORY")
        return self.APP_DIR / "data_league_db"

    SYNTH_DATA_DIR: Path = field(init=False)

    def __attrs_post_init__(self):
        self.SYNTH_DATA_DIR: Path = Path(self.MODULE_DIR) / "db/synthetic_data"

    def _module_to_os_path(self, module_name: str) -> str:
        """Get the string path of the module."""
        spec = find_spec(module_name)
        if not spec:
            raise ValueError(f"Couldn't find path for {module_name}")
        return str(Path(spec.origin).parent)  # type: ignore[arg-type]


@lru_cache
def get_settings() -> Settings:
    return Settings()
