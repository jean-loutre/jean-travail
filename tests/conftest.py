from typing import Iterator

from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture


@fixture(autouse=True)
def pomodoro(fs: Patcher) -> Iterator[None]:
    yield
