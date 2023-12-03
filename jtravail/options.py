from configparser import ConfigParser
from os import environ
from pathlib import Path
from typing import Any, Callable, TypeVar

from appdirs import user_config_dir

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
DEFAULT_CONFIG_FILE = Path(user_config_dir(_APP_NAME, _APP_AUTHOR)) / "config.cfg"


T = TypeVar("T")


class Options:
    def __init__(self, config_filename: Path | None = None) -> None:
        self._config_parser = ConfigParser()
        self._config_parser.read(config_filename or DEFAULT_CONFIG_FILE)

    def get(self, name: str, converter: Callable[[Any], T], default: T) -> T:
        try:
            config = dict(self._config_parser["options"])
        except KeyError:
            config = {}

        env_var = f"JTRAVAIL_{name.upper()}"

        if env_var in environ:
            return converter(environ[env_var])
        elif name in config:
            return converter(config[name])

        return default
