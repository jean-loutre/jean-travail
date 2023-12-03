from click.testing import CliRunner

from jtravail.cli import main


def test_stop() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["next"])
    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert result.output == "Stopped: 00:00\n"

    result = runner.invoke(main, ["stop"])

    assert result.exit_code == 0
    assert result.output == "Stopped: 00:00\n"
