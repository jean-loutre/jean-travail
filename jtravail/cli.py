from functools import wraps
from gettext import gettext as _
from pathlib import Path
from typing import Callable

from click import Context
from click import Path as ClickPath
from click import echo, group, option, pass_context, pass_obj

from jtravail.options import DEFAULT_CONFIG_FILE
from jtravail.pomodoro import Pomodoro


def print_status(command: Callable[[Pomodoro], None]) -> Callable[[Pomodoro], None]:
    @wraps(command)
    def _wrapper(pomodoro: Pomodoro) -> None:
        command(pomodoro)
        if pomodoro.stopped:
            status_name = _("Stopped")
        elif pomodoro.working:
            status_name = _("Working")
        elif pomodoro.paused:
            status_name = _("Paused")

        minutes = int(pomodoro.remaining.total_seconds() / 60)
        seconds = abs(int(pomodoro.remaining.total_seconds() - 60 * minutes))
        echo(
            _("{status}: {minutes:02d}:{seconds:02d}").format(
                status=status_name, minutes=minutes, seconds=seconds
            )
        )

    return _wrapper


@group()
@pass_context
@option(
    "-c",
    "--config",
    type=ClickPath(dir_okay=False, exists=True),
    show_default=str(DEFAULT_CONFIG_FILE),
    help=_("Path to configuration file"),
)
@option(
    "-w",
    "--work-duration",
    type=int,
    show_default="1500 : 25 minutes",
    help=_("Work session duration in seconds"),
)
def main(
    context: Context, config: Path | None = None, work_duration: int | None = None
) -> None:
    context.obj = Pomodoro(config_path=config, work_duration=work_duration)


@main.command()
@pass_obj
@print_status
def next(pomodoro: Pomodoro) -> None:
    pomodoro.next()


@main.command()
@pass_obj
@print_status
def status(pomodoro: Pomodoro) -> None:
    pass


@main.command()
@pass_obj
@print_status
def stop(pomodoro: Pomodoro) -> None:
    pomodoro.stop()
