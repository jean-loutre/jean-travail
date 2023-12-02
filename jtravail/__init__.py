from gettext import gettext as _

from click import echo, group

from jtravail.pomodoro import Pomodoro, Status


@group()
def cli() -> int:
    return 0


@cli.command()
def start() -> int:
    pomodoro = Pomodoro()
    pomodoro.start()
    echo(_("Pomodoro started"))
    return 0


@cli.command()
def status() -> int:
    pomodoro = Pomodoro()
    (status, remaining) = pomodoro.status()
    if status is Status.STOPPED:
        echo(_("stopped"))
    else:
        assert remaining is not None
        minutes = int(remaining.total_seconds() / 60)
        seconds = abs(int(remaining.total_seconds() - 60 * minutes))
        echo(
            _("Pomodoro : {minutes}:{seconds}").format(minutes=minutes, seconds=seconds)
        )

    return 0
