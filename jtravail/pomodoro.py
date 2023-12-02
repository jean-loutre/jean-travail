from datetime import datetime, timedelta
from enum import Enum
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path

from appdirs import user_cache_dir

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
_CACHE_DIR = Path(user_cache_dir(_APP_NAME, _APP_AUTHOR))


class Status(str, Enum):
    STOPPED = "stopped"
    POMODORO = "pomodoro"
    PAUSED = "paused"


class _Pomodoro:
    def __init__(self) -> None:
        self._state_path = _CACHE_DIR / "state"
        self._status = Status.STOPPED
        self._start_time: datetime | None = None
        self._pomodoro_duration: timedelta = timedelta(minutes=25)
        self._pause_duration: timedelta = timedelta(minutes=5)
        self.refresh()
        pass

    def start(self) -> None:
        self._status = Status.POMODORO
        self._start_time = datetime.now()
        self._save()

    def pause(self) -> None:
        self._status = Status.PAUSED
        self._start_time = datetime.now()
        self._save()

    def status(self) -> tuple[Status, timedelta | None]:
        remaining = None
        if self._start_time is not None:
            if self._status == Status.POMODORO:
                duration = self._pomodoro_duration
            else:
                duration = self._pause_duration
            elapsed = datetime.now() - self._start_time
            remaining = duration - elapsed
        return self._status, remaining

    def stop(self) -> None:
        try:
            self._state_path.unlink()
        except FileNotFoundError:
            pass
        self.refresh()

    def refresh(self) -> None:
        if not self._state_path.is_file():
            self._status = Status.STOPPED
            self._start_time = None
        else:
            with self._state_path.open("r") as state_file:
                data = json_loads(state_file.read() or "{}")
                self._status = data.get("status", "stopped")
                start_time_str = data.get("start_time", None)
                self._start_time = start_time_str and datetime.fromisoformat(
                    start_time_str
                )

    def _save(self) -> None:
        data = {
            "status": self._status,
            "start_time": self._start_time and self._start_time.isoformat(),
        }
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        with self._state_path.open("w") as state_file:
            state_file.write(json_dumps(data))


_POMODORO = _Pomodoro()

pause = _POMODORO.pause
refresh = _POMODORO.refresh
start = _POMODORO.start
status = _POMODORO.status
stop = _POMODORO.stop
