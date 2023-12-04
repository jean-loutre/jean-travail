from conftest import Cli


def test_status(cli: Cli) -> None:
    assert cli("status") == "1/4 Idle: 00:00\n"

    cli("next")
    assert cli("status") == "1/4 Work: 25:00\n"

    cli.tick(67)
    assert cli("status") == "1/4 Work: 23:53\n"

    cli.tick(25 * 60)
    assert cli("status") == "1/4 Work: -1:07\n"

    cli("next")
    assert cli("status") == "1/4 Pause: 05:00\n"

    cli.tick(67)
    assert cli("status") == "1/4 Pause: 03:53\n"

    cli.tick(5 * 60)
    assert cli("status") == "1/4 Pause: -1:07\n"


def test_work_duration_parameter(cli: Cli) -> None:
    with cli.config(work_duration="30"):
        cli("next")
        assert cli("status") == "1/4 Work: 30:00\n"

        with cli.environment(JTRAVAIL_WORK_DURATION="40"):
            cli("stop", "next")
            assert cli("status") == "1/4 Work: 40:00\n"

            cli("stop", "next")
            assert cli("status -w 50") == "1/4 Work: 50:00\n"
            assert cli("status --work-duration 50") == "1/4 Work: 50:00\n"


def test_pause_duration_parameter(cli: Cli) -> None:
    with cli.config(pause_duration="30"):
        cli("next", "next")
        assert cli("status") == "1/4 Pause: 30:00\n"

        with cli.environment(JTRAVAIL_PAUSE_DURATION="40"):
            cli("stop", "next", "next")
            assert cli("status") == "1/4 Pause: 40:00\n"

            cli("stop", "next", "next")
            assert cli("status -p 50") == "1/4 Pause: 50:00\n"
            assert cli("status --pause-duration 50") == "1/4 Pause: 50:00\n"


def test_format_parameter(cli: Cli) -> None:
    with cli.config(format="From config"):
        cli("next")
        assert cli("status") == "From config\n"

        with cli.environment(JTRAVAIL_STATUS_FORMAT="From env"):
            assert cli("status") == "From env\n"
            assert cli("status -f 'From command line'") == "From command line\n"
            assert cli("status --format 'From command line'") == "From command line\n"


def test_format_parameter_substitutions(cli: Cli) -> None:
    assert cli("status -f '{status}'") == "Idle\n"
    cli("next")
    assert cli("status -f '{status}'") == "Work\n"
    cli("next")
    assert cli("status -f '{status}'") == "Pause\n"

    assert cli("status -f '{minutes}'") == "5\n"
    assert cli("status -f '{seconds}'") == "0\n"
    assert cli("status -f '{total_seconds}'") == "300\n"
    assert cli("status -f '{iteration}'") == "1\n"
    assert cli("status -f '{long_pause_period}'") == "4\n"
