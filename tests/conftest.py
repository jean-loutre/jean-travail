from contextlib import contextmanager
from datetime import datetime
from os import environ
from typing import Iterator

from freezegun import freeze_time
from freezegun.api import FrozenDateTimeFactory, StepTickTimeFactory
from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

from jtravail.options import DEFAULT_CONFIG_FILE

Freezer = FrozenDateTimeFactory | StepTickTimeFactory


@fixture(autouse=True)
def freezer(fs: Patcher) -> Iterator[Freezer]:
    with freeze_time(datetime.now()) as freezer:
        yield freezer


@contextmanager
def set_config(**parameters: str) -> Iterator[None]:
    DEFAULT_CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
    with open(DEFAULT_CONFIG_FILE, "w") as config_file:
        config_file.write("[options]\n")
        for key, value in parameters.items():
            config_file.write(f"{key}={value}\n")

    yield

    DEFAULT_CONFIG_FILE.unlink()


@contextmanager
def set_environment(**parameters: str) -> Iterator[None]:
    old_environ = {}
    for key, value in parameters.items():
        old_value = environ.get(key)
        if old_value is not None:
            old_environ[key] = old_value
        environ[key] = value

    yield

    for key in parameters.keys():
        del environ[key]

    for key, value in old_environ.items():
        environ[key] = value
