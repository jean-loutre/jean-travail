from datetime import datetime, timedelta

from click.testing import CliRunner
from freezegun import freeze_time

from jtravail import cli


def test_status() -> None:
    runner = CliRunner()
    with freeze_time(datetime.now()) as frozen_datetime:
        runner.invoke(cli, ["start"])

        frozen_datetime.tick(delta=timedelta(seconds=10))
        result = runner.invoke(cli, ["status"])
        assert "Pomodoro : 24:50" in result.output

        frozen_datetime.tick(delta=timedelta(minutes=30))
        result = runner.invoke(cli, ["status"])
        assert "Pomodoro : -5:10" in result.output
