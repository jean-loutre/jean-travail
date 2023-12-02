from datetime import timedelta
from functools import wraps
from gettext import gettext as _
from typing import Callable

from click import Context, echo, group, option, pass_context, pass_obj

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
@option(
    "-w",
    "--work-duration",
    default=25 * 60,
    show_default=True,
    help=_("Work session duration in seconds"),
)
@pass_context
def main(context: Context, work_duration: int) -> None:
    context.obj = Pomodoro(work_duration=timedelta(seconds=work_duration))


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
