from datetime import timedelta
from unittest.mock import Mock, patch

from click.testing import CliRunner

from jtravail import pomodoro
from jtravail.cli import main


@patch("jtravail.pomodoro.start")
def test_start(mock_start: Mock) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["start"])

    assert result.exit_code == 0
    assert mock_start.called_once()
    assert result.output == "Pomodoro started\n"


@patch("jtravail.pomodoro.status")
def test_status(mock_status: Mock) -> None:
    runner = CliRunner()

    mock_status.return_value = (pomodoro.Status.STOPPED, None)
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Stopped\n"

    mock_status.return_value = (pomodoro.Status.POMODORO, timedelta(seconds=65))
    result = runner.invoke(main, ["status"])

    assert result.exit_code == 0
    assert result.output == "Pomodoro : 01:05\n"