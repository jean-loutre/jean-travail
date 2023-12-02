from datetime import timedelta
from unittest.mock import Mock, patch

from click.testing import CliRunner

from jtravail.cli import main
from jtravail.pomodoro import Status


@patch("jtravail.pomodoro.start")
def test_start(mock_start: Mock) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["start"])

    assert result.exit_code == 0
    assert mock_start.called_once()
    assert result.output == "Pomodoro started\n"


@patch("jtravail.pomodoro.pause")
def test_pause(mock_pause: Mock) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["pause"])

    assert result.exit_code == 0
    assert mock_pause.called_once()
    assert result.output == "Pomodoro paused\n"


@patch("jtravail.pomodoro.status")
def test_status(mock_status: Mock) -> None:
    runner = CliRunner()

    mock_status.return_value = Status(Status.STOPPED, None)
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Stopped\n"

    mock_status.return_value = Status(Status.POMODORO, timedelta(seconds=65))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Pomodoro : 01:05\n"

    mock_status.return_value = Status(Status.PAUSED, timedelta(seconds=65))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Pause : 01:05\n"


@patch("jtravail.pomodoro.stop")
def test_stop(mock_start: Mock) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert mock_start.called_once()
    assert result.output == "Pomodoro stopped\n"
