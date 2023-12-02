from typing import Iterator

from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

from jtravail.pomodoro import Pomodoro


@fixture(autouse=True)
def pomodoro(fs: Patcher) -> Iterator[Pomodoro]:
    yield Pomodoro()
