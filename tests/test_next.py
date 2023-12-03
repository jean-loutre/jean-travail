from click.testing import CliRunner
from conftest import set_config, set_environment

from jtravail.cli import main


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


def test_work_duration_parameter() -> None:
    runner = CliRunner()
    with set_config(work_duration=str(30 * 60)):
        result = runner.invoke(main, ["next"])
        assert result.exit_code == 0
        assert result.output == "Working: 30:00\n"

        with set_environment(JTRAVAIL_WORK_DURATION=str(40 * 60)):
            runner.invoke(main, ["stop"])
            result = runner.invoke(main, ["next"])
            assert result.exit_code == 0
            assert result.output == "Working: 40:00\n"

            runner.invoke(main, ["stop"])
            result = runner.invoke(main, ["next", "-w", str(50 * 60)])
            assert result.exit_code == 0
            assert result.output == "Working: 50:00\n"
