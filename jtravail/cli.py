from gettext import gettext as _

from click import echo, group

from jtravail import pomodoro


@group()
def main() -> int:
    return 0


@main.command()
def start() -> int:
    pomodoro.start()
    echo(_("Pomodoro started"))
    return 0


@main.command()
def status() -> int:
    (status, remaining) = pomodoro.status()
    if status is pomodoro.Status.STOPPED:
        echo(_("Stopped"))
    else:
        assert remaining is not None
        minutes = int(remaining.total_seconds() / 60)
        seconds = abs(int(remaining.total_seconds() - 60 * minutes))
        echo(
            _("Pomodoro : {minutes:02d}:{seconds:02d}").format(
                minutes=minutes, seconds=seconds
            )
        )

    return 0


@main.command()
def stop() -> int:
    pomodoro.stop()
    echo(_("Pomodoro stopped"))
    return 0
