from datetime import datetime
from typing import Iterator

from freezegun import freeze_time
from freezegun.api import FrozenDateTimeFactory, StepTickTimeFactory
from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

Freezer = FrozenDateTimeFactory | StepTickTimeFactory


@fixture(autouse=True)
def freezer(fs: Patcher) -> Iterator[Freezer]:
    with freeze_time(datetime.now()) as freezer:
        yield freezer
