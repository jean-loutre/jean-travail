from functools import wraps
from gettext import gettext as _
from typing import Callable

from click import Context, echo, group, pass_context, pass_obj

from jtravail.pomodoro import Pomodoro


def print_status(command: Callable[[Pomodoro], None]) -> Callable[[Pomodoro], None]:
    @wraps(command)
    def _wrapper(pomodoro: Pomodoro) -> None:
        command(pomodoro)
        if pomodoro.stopped:
            status_name = _("Stopped")
        elif pomodoro.running:
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
def main(context: Context) -> None:
    context.obj = Pomodoro()


@main.command()
@pass_obj
@print_status
def start(pomodoro: Pomodoro) -> None:
    pomodoro.start()


@main.command()
@pass_obj
@print_status
def pause(pomodoro: Pomodoro) -> None:
    pomodoro.pause()


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
