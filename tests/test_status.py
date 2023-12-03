from conftest import Cli


def test_status(cli: Cli) -> None:
    assert cli("status") == "Stopped: 00:00\n"

    cli("next")
    assert cli("status") == "Working: 25:00\n"

    cli.tick(67)
    assert cli("status") == "Working: 23:53\n"

    cli.tick(25 * 60)
    assert cli("status") == "Working: -1:07\n"

    cli("next")
    assert cli("status") == "Paused: 05:00\n"

    cli.tick(67)
    assert cli("status") == "Paused: 03:53\n"

    cli.tick(5 * 60)
    assert cli("status") == "Paused: -1:07\n"


def test_work_duration_parameter(cli: Cli) -> None:
    with cli.config(work_duration="30"):
        cli("next")
        assert cli("status") == "Working: 30:00\n"

        with cli.environment(JTRAVAIL_WORK_DURATION="40"):
            cli("stop")
            cli("next")
            assert cli("status") == "Working: 40:00\n"

            cli("stop")
            cli("next")
            assert cli("status -w 50") == "Working: 50:00\n"
            assert cli("status --work-duration 50") == "Working: 50:00\n"
