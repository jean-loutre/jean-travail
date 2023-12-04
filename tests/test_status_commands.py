from conftest import Cli
from pytest import mark

from jtravail.pomodoro import DEFAULT_STATE_FILE


@mark.parametrize(
    "commands",
    [
        ["stop", "next"],
        ["stop", "next", "status"],
    ],
)
def test_work_duration_parameter(cli: Cli, commands: list[str]) -> None:
    with cli.config(work_duration="30"):
        assert cli(*commands) == "1/4 Work: 30:00\n"

        with cli.environment(JTRAVAIL_WORK_DURATION="40"):
            assert cli(*commands) == "1/4 Work: 40:00\n"
            last_command = commands.pop()

            assert cli(*commands, f"{last_command} -w 50") == "1/4 Work: 50:00\n"
            assert (
                cli(*commands, f"{last_command} --work-duration 50")
                == "1/4 Work: 50:00\n"
            )


@mark.parametrize(
    "commands",
    [
        ["stop", "next", "next"],
        ["stop", "next", "next", "status"],
    ],
)
def test_pause_duration_parameter(cli: Cli, commands: list[str]) -> None:
    with cli.config(pause_duration="30"):
        assert cli(*commands) == "1/4 Pause: 30:00\n"

        with cli.environment(JTRAVAIL_PAUSE_DURATION="40"):
            assert cli(*commands) == "1/4 Pause: 40:00\n"
            last_command = commands.pop()

            assert cli(*commands, f"{last_command} -p 50") == "1/4 Pause: 50:00\n"
            assert (
                cli(*commands, f"{last_command} --pause-duration 50")
                == "1/4 Pause: 50:00\n"
            )


@mark.parametrize(
    "commands",
    [
        ["stop"] + ["next"] * 8,
        ["stop"] + ["next"] * 8 + ["status"],
    ],
)
def test_long_pause_duration_parameter(cli: Cli, commands: list[str]) -> None:
    def _work_to_long_pause() -> None:
        cli("stop")
        for _ in range(0, 8):
            cli("next")

    with cli.config(long_pause_duration="30"):
        cli(*commands)
        assert cli("status") == "4/4 Long Pause: 30:00\n"

        with cli.environment(JTRAVAIL_LONG_PAUSE_DURATION="40"):
            cli(*commands)
            assert cli("status") == "4/4 Long Pause: 40:00\n"

            last_command = commands.pop()

            assert cli(*commands, f"{last_command} -l 50") == "4/4 Long Pause: 50:00\n"
            assert (
                cli(*commands, f"{last_command} --long-pause-duration 50")
                == "4/4 Long Pause: 50:00\n"
            )


@mark.parametrize(
    "commands",
    [
        ["stop", "next", "next"],
        ["stop", "next", "next", "status"],
    ],
)
def test_long_pause_period_parameter(cli: Cli, commands: list[str]) -> None:
    with cli.config(long_pause_period="2"):
        assert cli(*commands) == "1/2 Pause: 05:00\n"

        with cli.environment(JTRAVAIL_LONG_PAUSE_PERIOD="3"):
            assert cli(*commands) == "1/3 Pause: 05:00\n"

            last_command = commands.pop()

            assert cli(*commands, f"{last_command} -P 5") == "1/5 Pause: 05:00\n"
            assert (
                cli(*commands, f"{last_command} --long-pause-period 5")
                == "1/5 Pause: 05:00\n"
            )


@mark.parametrize(
    "command",
    [
        "next",
        "status",
    ],
)
def test_format_parameter(cli: Cli, command: str) -> None:
    with cli.config(format="From config"):
        assert cli(command) == "From config\n"

        with cli.environment(JTRAVAIL_STATUS_FORMAT="From env"):
            assert cli(command) == "From env\n"
            assert cli(f"{command} -f 'From command line'") == "From command line\n"
            assert (
                cli(f"{command} --format 'From command line'") == "From command line\n"
            )


@mark.parametrize(
    "command,status_text",
    [
        ("next", "1/4 Work: 25:00\n"),
        ("status", "1/4 Idle: 00:00\n"),
    ],
)
def test_state_file_errors(cli: Cli, command: str, status_text: str) -> None:
    DEFAULT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _write_state(content: str) -> None:
        with DEFAULT_STATE_FILE.open("w") as state_file:
            state_file.write(content)

    _write_state("not json")
    assert cli(command) == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: "
        + "Parse error : Expecting value: line 1 column 1 (char 0). "
        + "State was reset.\n"
        + status_text
    )

    _write_state("[]")
    assert cli(command) == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: Unexpected content. State was reset.\n"
        + status_text
    )

    _write_state(
        """{
        "status": "unknown_status"
    }"""
    )
    assert cli(command) == (
        f'Error while loading state file {DEFAULT_STATE_FILE}: Unknown status "unknown_status". '
        + "State was reset.\n"
        + status_text
    )

    _write_state("""{ "status": "work"}""")
    assert cli(command) == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: No start time defined. "
        + "State was reset.\n"
        + status_text
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "fucked_up_start_time"
    }"""
    )
    assert cli(command) == (
        f'Error while loading state file {DEFAULT_STATE_FILE}: Invalid start time "fucked_up_start_time". '
        + "State was reset.\n"
        + status_text
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "2022-01-01"
    }"""
    )
    assert cli(command) == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: No iteration defined. "
        + "State was reset.\n"
        + status_text
    )

    _write_state(
        """{
        "status": "work",
        "start_time": "2022-01-01",
        "iteration": "fucked_up_iteration"
    }"""
    )
    assert cli(command) == (
        f"Error while loading state file {DEFAULT_STATE_FILE}: "
        + 'Invalid iteration format "fucked_up_iteration". '
        + "State was reset.\n"
        + status_text
    )
