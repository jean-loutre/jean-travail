from conftest import Cli


def test_next(cli: Cli) -> None:
    assert cli("next") == "Working: 25:00\n"
    assert cli("next") == "Paused: 05:00\n"
    assert cli("next") == "Working: 25:00\n"


def test_work_duration_parameter(cli: Cli) -> None:
    with cli.config(work_duration="30"):
        assert cli("next") == "Working: 30:00\n"

        with cli.environment(JTRAVAIL_WORK_DURATION="40"):
            cli("stop")
            assert cli("next") == "Working: 40:00\n"

            cli("stop")
            assert cli("next -w 50") == "Working: 50:00\n"

            cli("stop")
            assert cli("next --work-duration 50") == "Working: 50:00\n"
