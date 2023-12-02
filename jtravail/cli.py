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
def pause() -> int:
    pomodoro.pause()
    echo(_("Pomodoro paused"))
    return 0


@main.command()
def status() -> int:
    status = pomodoro.status()
    if status.stopped:
        echo(_("Stopped"))
    else:
        assert status.remaining is not None
        minutes = int(status.remaining.total_seconds() / 60)
        seconds = abs(int(status.remaining.total_seconds() - 60 * minutes))
        status_name = "Pomodoro" if status.pomodoro else "Pause"
        echo(
            _("{status} : {minutes:02d}:{seconds:02d}").format(
                status=status_name, minutes=minutes, seconds=seconds
            )
        )

    return 0


@main.command()
def stop() -> int:
    pomodoro.stop()
    echo(_("Pomodoro stopped"))
    return 0
