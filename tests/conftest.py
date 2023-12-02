from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

from jtravail import pomodoro as _pomodoro


@fixture(autouse=True)
def pomodoro(fs: Patcher) -> None:
    _pomodoro.refresh()
