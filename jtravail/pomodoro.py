from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import cached_property
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from typing import Iterable, Iterator

from appdirs import user_cache_dir, user_data_dir

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
_CACHE_DIR = Path(user_cache_dir(_APP_NAME, _APP_AUTHOR))
_DATA_DIR = Path(user_data_dir(_APP_NAME, _APP_AUTHOR))


class LogEntry:
    def __init__(self, line: str) -> None:
        self._line = line.strip()

    @cached_property
    def start(self) -> datetime:
        return datetime.fromisoformat(self._columns[0])

    @cached_property
    def end(self) -> datetime:
        return datetime.fromisoformat(self._columns[1])

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    @cached_property
    def type(self) -> str:
        return self._columns[2]

    @cached_property
    def _columns(self) -> list[str]:
        return self._line.split(sep=";", maxsplit=3)


class Status:
    STOPPED = "stopped"
    POMODORO = "pomodoro"
    PAUSED = "paused"

    def __init__(self, state: str, remaining: timedelta | None) -> None:
        self._state = state
        self._remaining = remaining

    @property
    def stopped(self) -> bool:
        return self._state == self.STOPPED

    @property
    def pomodoro(self) -> bool:
        return self._state == self.POMODORO

    @property
    def paused(self) -> bool:
        return self._state == self.PAUSED

    @property
    def remaining(self) -> timedelta | None:
        return self._remaining


class _Pomodoro:
    def __init__(self) -> None:
        self._state_path = _CACHE_DIR / "state"
        self._log_path = _DATA_DIR / "log.db"

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
        self._push_log()
        self._status = Status.PAUSED
        self._start_time = datetime.now()
        self._save()

    def status(self) -> Status:
        remaining = None
        if self._start_time is not None:
            if self._status == Status.POMODORO:
                duration = self._pomodoro_duration
            else:
                duration = self._pause_duration
            elapsed = datetime.now() - self._start_time
            remaining = duration - elapsed
        return Status(self._status, remaining)

    @contextmanager
    def get_log(self) -> Iterator[Iterable[LogEntry]]:
        try:
            with self._log_path.open("r") as log:

                def _iterate_log() -> Iterator[LogEntry]:
                    for line in log.readlines():
                        yield LogEntry(line)

                yield _iterate_log()
        except FileNotFoundError:
            yield []

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

    def _push_log(self) -> None:
        if self._status not in [Status.POMODORO, Status.PAUSED]:
            return

        if not self._log_path.exists():
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

        assert self._start_time is not None
        start = self._start_time.isoformat()
        end = datetime.now().isoformat()

        with self._log_path.open("a") as log_file:
            log_file.write(f"{start};{end};{self._status}\n")

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
get_log = _POMODORO.get_log
