from contextlib import contextmanager
from datetime import datetime, timedelta
from os import environ
from shlex import split
from typing import Iterator

from click.testing import CliRunner
from freezegun import freeze_time
from freezegun.api import FrozenDateTimeFactory, StepTickTimeFactory
from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

from jtravail.cli import DEFAULT_CONFIG_FILE, main


class Cli:
    def __init__(self, freezer: FrozenDateTimeFactory | StepTickTimeFactory) -> None:
        self._freezer = freezer

    def __call__(self, *commands: str) -> str:
        for command in commands:
            runner = CliRunner()
            result = runner.invoke(main, split(command))
            if result.exception is not None:
                raise result.exception

        return result.output

    def tick(self, seconds: int) -> None:
        self._freezer.tick(delta=timedelta(seconds=seconds))

    @contextmanager
    def config(self, **parameters: str) -> Iterator[None]:
        DEFAULT_CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
        with open(DEFAULT_CONFIG_FILE, "w") as config_file:
            config_file.write("[options]\n")
            for key, value in parameters.items():
                config_file.write(f"{key}={value}\n")

        yield

        DEFAULT_CONFIG_FILE.unlink()

    @contextmanager
    def environment(self, **parameters: str) -> Iterator[None]:
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


@fixture(autouse=True)
def cli(fs: Patcher) -> Iterator[Cli]:
    with freeze_time(datetime.now()) as freezer:
        yield Cli(freezer)
