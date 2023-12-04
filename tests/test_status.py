from conftest import Cli


def test_status(cli: Cli) -> None:
    assert cli("status") == "1/4 Idle: 00:00\n"

    cli("next")
    assert cli("status") == "1/4 Work: 25:00\n"

    cli.tick(67)
    assert cli("status") == "1/4 Work: 23:53\n"

    cli.tick(25 * 60)
    assert cli("status") == "1/4 Work: -01:07\n"

    cli("next")
    assert cli("status") == "1/4 Pause: 05:00\n"

    cli.tick(67)
    assert cli("status") == "1/4 Pause: 03:53\n"

    cli.tick(5 * 60)
    assert cli("status") == "1/4 Pause: -01:07\n"


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
