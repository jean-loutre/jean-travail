from datetime import datetime
from gettext import gettext as _
from json import dumps as json_dumps
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
