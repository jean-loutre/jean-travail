from datetime import datetime, timedelta

from click.testing import CliRunner
from freezegun import freeze_time

from jtravail.cli import main


def test_start() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["start"])

    assert result.exit_code == 0
    assert result.output == "Pomodoro started\n"


def test_pause() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["pause"])

    assert result.exit_code == 0
    assert result.output == "Pomodoro paused\n"


def test_status() -> None:
    with freeze_time(datetime.now()) as frozen_datetime:
        runner = CliRunner()

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Stopped\n"

        result = runner.invoke(main, ["start"])

        frozen_datetime.tick(delta=timedelta(seconds=24 * 60))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Pomodoro : 01:00\n"

        result = runner.invoke(main, ["pause"])
        frozen_datetime.tick(delta=timedelta(seconds=4 * 60))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Pause : 01:00\n"


def test_stop() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert result.output == "Pomodoro stopped\n"
