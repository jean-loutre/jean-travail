from gettext import gettext as _

from click import Context, echo, group, pass_context, pass_obj

from jtravail.pomodoro import Pomodoro


@group()
@pass_context
def main(context: Context) -> int:
    context.obj = Pomodoro()
    return 0


@main.command()
@pass_obj
def start(pomodoro: Pomodoro) -> int:
    pomodoro.start()
    echo(_("Pomodoro started"))
    return 0


@main.command()
@pass_obj
def pause(pomodoro: Pomodoro) -> int:
    pomodoro.pause()
    echo(_("Pomodoro paused"))
    return 0


@main.command()
@pass_obj
def status(pomodoro: Pomodoro) -> int:
    if pomodoro.stopped:
        echo(_("Stopped"))
    else:
        minutes = int(pomodoro.remaining.total_seconds() / 60)
        seconds = abs(int(pomodoro.remaining.total_seconds() - 60 * minutes))
        status_name = "Pomodoro" if pomodoro.running else "Pause"
        echo(
            _("{status} : {minutes:02d}:{seconds:02d}").format(
                status=status_name, minutes=minutes, seconds=seconds
            )
        )

    return 0


@main.command()
@pass_obj
def stop(pomodoro: Pomodoro) -> int:
    pomodoro.stop()
    echo(_("Pomodoro stopped"))
    return 0
