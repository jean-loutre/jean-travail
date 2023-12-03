from contextlib import contextmanager
from datetime import timedelta
from os import environ
from typing import Iterator

from click.testing import CliRunner
from conftest import Freezer

from jtravail.cli import main
from jtravail.options import DEFAULT_CONFIG_FILE


def test_next() -> None:
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


def test_status(freezer: Freezer) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Stopped: 00:00\n"

    result = runner.invoke(main, ["next"])
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Working: 25:00\n"

    freezer.tick(delta=timedelta(seconds=67))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Working: 23:53\n"

    freezer.tick(delta=timedelta(seconds=25 * 60))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Working: -1:07\n"

    result = runner.invoke(main, ["next"])
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Paused: 05:00\n"

    freezer.tick(delta=timedelta(seconds=67))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Paused: 03:53\n"

    freezer.tick(delta=timedelta(seconds=5 * 60))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Paused: -1:07\n"


def test_stop() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["next"])
    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert result.output == "Stopped: 00:00\n"

    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert result.output == "Stopped: 00:00\n"


@contextmanager
def set_config(**parameters: str) -> Iterator[None]:
    DEFAULT_CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
    with open(DEFAULT_CONFIG_FILE, "w") as config_file:
        config_file.write("[options]\n")
        for key, value in parameters.items():
            config_file.write(f"{key}={value}\n")

    yield


def test_work_duration_parameter() -> None:
    runner = CliRunner()
    with set_config(work_duration=str(30 * 60)):
        result = runner.invoke(main, ["next"])
        assert result.exit_code == 0
        assert result.output == "Working: 30:00\n"

        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert result.output == "Working: 30:00\n"

        runner.invoke(main, ["stop"])
        environ["JTRAVAIL_WORK_DURATION"] = str(40 * 60)
        result = runner.invoke(main, ["next"])
        assert result.exit_code == 0
        assert result.output == "Working: 40:00\n"

        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert result.output == "Working: 40:00\n"

        runner.invoke(main, ["stop"])
        result = runner.invoke(main, ["-w", str(50 * 60), "next"])
        assert result.exit_code == 0
        assert result.output == "Working: 50:00\n"

        result = runner.invoke(main, ["-w", str(50 * 60), "status"])
        assert result.exit_code == 0
        assert result.output == "Working: 50:00\n"
