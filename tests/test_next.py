from conftest import Cli


def test_next(cli: Cli) -> None:
    assert cli("next") == "Work: 25:00\n"
    assert cli("next") == "Pause: 05:00\n"
    assert cli("next") == "Work: 25:00\n"


def test_work_duration_parameter(cli: Cli) -> None:
    with cli.config(work_duration="30"):
        assert cli("next") == "Work: 30:00\n"

        with cli.environment(JTRAVAIL_WORK_DURATION="40"):
            cli("stop")
            assert cli("next") == "Work: 40:00\n"

            cli("stop")
            assert cli("next -w 50") == "Work: 50:00\n"

            cli("stop")
            assert cli("next --work-duration 50") == "Work: 50:00\n"


def test_pause_duration_parameter(cli: Cli) -> None:
    with cli.config(pause_duration="30"):
        cli("next")
        assert cli("next") == "Pause: 30:00\n"

        with cli.environment(JTRAVAIL_PAUSE_DURATION="40"):
            cli("stop", "next")
            assert cli("next") == "Pause: 40:00\n"

            cli("stop", "next")
            assert cli("next -p 50") == "Pause: 50:00\n"

            cli("stop", "next")
            assert cli("next --pause-duration 50") == "Pause: 50:00\n"


def test_format_parameter(cli: Cli) -> None:
    with cli.config(format="From config"):
        assert cli("next") == "From config\n"

        with cli.environment(JTRAVAIL_STATUS_FORMAT="From env"):
            assert cli("next") == "From env\n"
            assert cli("next -f 'From command line'") == "From command line\n"
            assert cli("next --format 'From command line'") == "From command line\n"


def test_format_parameter_substitutions(cli: Cli) -> None:
    assert cli("next -f '{status}'") == "Work\n"
    assert cli("next -f '{status}'") == "Pause\n"
    assert cli("stop", "next -f '{minutes} {seconds} {total_seconds}'") == "25 0 1500\n"
