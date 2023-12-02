from click.testing import CliRunner

from jtravail import cli


def test_start() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["start"])
    assert result.exit_code == 0
    assert "Pomodoro started" in result.output
