from conftest import Cli


def test_next(cli: Cli) -> None:
    assert cli("next") == "1/4 Work: 25:00\n"
    assert cli("next") == "1/4 Pause: 05:00\n"
    assert cli("next") == "2/4 Work: 25:00\n"
    assert cli("next", "next", "next", "next", "next") == "4/4 Long Pause: 15:00\n"
    assert cli("next") == "1/4 Work: 25:00\n"


def test_format_parameter_substitutions(cli: Cli) -> None:
    assert cli("next -f '{status}'") == "Work\n"
    assert cli("next -f '{status}'") == "Pause\n"
    assert cli("stop", "next -f '{minutes}'") == "25\n"
    assert cli("stop", "next -f '{seconds}'") == "0\n"
    assert cli("stop", "next -f '{total_seconds}'") == "1500\n"
    assert cli("stop", "next -f '{iteration}'") == "1\n"
    assert cli("stop", "next -f '{long_pause_period}'") == "4\n"
