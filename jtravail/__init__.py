from datetime import datetime, timedelta
from gettext import gettext as _
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path

from appdirs import user_cache_dir
from click import echo, group

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
_CACHE_DIR = Path(user_cache_dir(_APP_NAME, _APP_AUTHOR))


@group()
def cli() -> int:
    return 0


@cli.command()
def start() -> int:
    data = json_dumps({"started": datetime.now().isoformat()})
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_DIR / "current", "w") as cache_file:
        cache_file.write(data)

    echo(_("Pomodoro started"))
    return 0


@cli.command()
def status() -> int:
    cache_file = _CACHE_DIR / "current"
    if not cache_file.is_file():
        echo(_("stopped"))
    else:
        with open(cache_file, "r") as cache:
            data = json_loads(cache.read())
            started = datetime.fromisoformat(data["started"])
            elapsed = datetime.now() - started
            remaining = timedelta(minutes=25) - elapsed
            minutes = int(remaining.total_seconds() / 60)
            seconds = abs(int(remaining.total_seconds() - 60 * minutes))
            echo(
                _("Pomodoro : {minutes}:{seconds}").format(
                    minutes=minutes, seconds=seconds
                )
            )

    return 0
