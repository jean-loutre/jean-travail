from conftest import Cli


def test_stop(cli: Cli) -> None:
    cli("next")
    assert cli("stop") == "1/4 Idle: 00:00\n"

    # check stopping two times don't crash
    assert cli("stop") == "1/4 Idle: 00:00\n"
