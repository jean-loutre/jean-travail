from conftest import Cli

from jtravail.pomodoro import DEFAULT_STATE_FILE


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


def test_long_pause_duration_parameter(cli: Cli) -> None:
    def _work_to_long_pause() -> None:
        cli("stop")
        for _ in range(0, 8):
            cli("next")

    with cli.config(long_pause_duration="30"):
        _work_to_long_pause()
        assert cli("status") == "4/4 Long Pause: 30:00\n"

        with cli.environment(JTRAVAIL_LONG_PAUSE_DURATION="40"):
            _work_to_long_pause()
            assert cli("status") == "4/4 Long Pause: 40:00\n"

            _work_to_long_pause()
            assert cli("status -l 50") == "4/4 Long Pause: 50:00\n"
            assert cli("status --long-pause-duration 50") == "4/4 Long Pause: 50:00\n"


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


def test_state_file_errors(cli: Cli) -> None:
    DEFAULT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _write_state(content: str) -> None:
        with DEFAULT_STATE_FILE.open("w") as state_file:
            state_file.write(content)

    _write_state("not json")
    assert cli("status") == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: "
        + "Parse error : Expecting value: line 1 column 1 (char 0). "
        + "State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )

    _write_state("[]")
    assert cli("status") == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: Unexpected content. State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )

    _write_state(
        """{
        "status": "unknown_status"
    }"""
    )
    assert cli("status") == (
        f'Error while loading state file {DEFAULT_STATE_FILE}: Unknown status "unknown_status". '
        + "State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )

    _write_state("""{ "status": "work"}""")
    assert cli("status") == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: No start time defined. "
        + "State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "fucked_up_start_time"
    }"""
    )
    assert cli("status") == (
        f'Error while loading state file {DEFAULT_STATE_FILE}: Invalid start time "fucked_up_start_time". '
        + "State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "2022-01-01"
    }"""
    )
    assert cli("status") == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: No iteration defined. "
        + "State was reset.\n"
        "1/4 Idle: 00:00\n"
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "2022-01-01",
        "iteration": "fucked_up_iteration"
    }"""
    )
    assert cli("status") == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: "
        + 'Invalid iteration format "fucked_up_iteration". '
        + "State was reset.\n"
        + "1/4 Idle: 00:00\n"
    )
