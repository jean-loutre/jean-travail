from datetime import datetime, timedelta

from click.testing import CliRunner
from freezegun import freeze_time

from jtravail.cli import main


def test_next() -> None:
    with freeze_time(datetime.now()):
        runner = CliRunner()
        result = runner.invoke(main, ["next"])

        assert result.exit_code == 0
        assert result.output == "Working: 25:00\n"

        result = runner.invoke(main, ["next"])

        assert result.exit_code == 0
        assert result.output == "Paused: 05:00\n"

        result = runner.invoke(main, ["next"])

        assert result.exit_code == 0
        assert result.output == "Working: 25:00\n"


def test_status() -> None:
    with freeze_time(datetime.now()) as freeze:
        runner = CliRunner()
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Stopped: 00:00\n"

        result = runner.invoke(main, ["next"])
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Working: 25:00\n"

        freeze.tick(delta=timedelta(seconds=67))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Working: 23:53\n"

        freeze.tick(delta=timedelta(seconds=25 * 60))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Working: -1:07\n"

        result = runner.invoke(main, ["next"])
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Paused: 05:00\n"

        freeze.tick(delta=timedelta(seconds=67))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Paused: 03:53\n"

        freeze.tick(delta=timedelta(seconds=5 * 60))
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert result.output == "Paused: -1:07\n"


def test_stop() -> None:
    with freeze_time(datetime.now()):
        runner = CliRunner()
        result = runner.invoke(main, ["next"])
        result = runner.invoke(main, ["stop"])

        assert result.exit_code == 0
        assert result.output == "Stopped: 00:00\n"

        result = runner.invoke(main, ["stop"])

        assert result.exit_code == 0
        assert result.output == "Stopped: 00:00\n"
