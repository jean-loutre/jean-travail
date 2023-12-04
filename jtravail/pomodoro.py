from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import cached_property
from gettext import gettext as _
from json import JSONDecodeError
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from appdirs import user_cache_dir, user_data_dir
from click import echo

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
_CACHE_DIR = Path(user_cache_dir(_APP_NAME, _APP_AUTHOR))
_DATA_DIR = Path(user_data_dir(_APP_NAME, _APP_AUTHOR))
DEFAULT_STATE_FILE = _CACHE_DIR / "state"


class StateError(Exception):
    pass


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


_IDLE = "idle"
_WORK = "work"
_PAUSE = "pause"
_LONG_PAUSE = "long-pause"

_TRANSITIONS: dict[str, Callable[[int, int], tuple[str, int]]] = {
    _IDLE: lambda _, __: (_WORK, 1),
    _WORK: lambda iteration, period: (
        (_PAUSE if iteration % period else _LONG_PAUSE),
        iteration,
    ),
    _PAUSE: lambda iteration, _: (_WORK, iteration + 1),
    _LONG_PAUSE: lambda iteration, period: (
        _WORK,
        iteration + 1 if iteration % period else 1,
    ),
}


class Pomodoro:
    def __init__(self, config_path: Path | None = None) -> None:
        self._state_path = DEFAULT_STATE_FILE
        self._log_path = _DATA_DIR / "log.db"

        self._status = _IDLE
        self._start_time: datetime | None = None
        self._iteration = 1
        self._refresh()

    @property
    def idle(self) -> bool:
        return self._status == _IDLE

    @property
    def work(self) -> bool:
        return self._status == _WORK

    @property
    def pause(self) -> bool:
        return self._status == _PAUSE

    @property
    def long_pause(self) -> bool:
        return self._status == _LONG_PAUSE

    @property
    def iteration(self) -> int:
        return self._iteration

    def get_remaining_time(
        self,
        work_duration: int = 25,
        pause_duration: int = 5,
        long_pause_duration: int = 15,
    ) -> timedelta:
        if self._start_time is None:
            return timedelta(0)

        if self._status == _WORK:
            duration = work_duration
        elif self._status == _PAUSE:
            duration = pause_duration
        elif self._status == _LONG_PAUSE:
            duration = long_pause_duration
        else:
            assert False

        return timedelta(minutes=duration) - (datetime.now() - self._start_time)

    def next(self, long_pause_period: int = 4) -> None:
        if self._status is not _IDLE:
            self._push_log()
        (self._status, self._iteration) = _TRANSITIONS[self._status](
            self._iteration, long_pause_period
        )
        self._start_time = datetime.now()
        self._save()

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
        self._refresh()

    def _load_status(self, data: dict[str, Any]) -> None:
        self._status = data.get("status", _IDLE)

        if self._status not in [_IDLE, _WORK, _PAUSE, _LONG_PAUSE]:
            raise StateError(_('Unknown status "%s"') % self._status)

    def _load_start_time(self, data: dict[str, Any]) -> None:
        try:
            self._start_time = datetime.fromisoformat(data["start_time"])
        except KeyError:
            raise StateError(_("No start time defined"))
        except ValueError:
            raise StateError(_('Invalid start time "%s"') % data["start_time"])

    def _load_iteration(self, data: dict[str, Any]) -> None:
        try:
            self._iteration = int(data["iteration"])
        except KeyError:
            raise StateError(_("No iteration defined"))
        except ValueError:
            raise StateError(_('Invalid iteration format "%s"') % data["iteration"])

    def _refresh(self) -> None:
        try:
            with self._state_path.open("r") as state_file:
                try:
                    data = json_loads(state_file.read() or "{}")
                except JSONDecodeError as ex:
                    raise StateError(_("Parse error : %s") % ex)

            if not isinstance(data, dict):
                raise StateError(_("Unexpected content"))

            self._start_time = None
            self._iteration = 1

            self._load_status(data)
            if self._status is not _IDLE:
                self._load_start_time(data)
                self._load_iteration(data)
        except FileNotFoundError:
            self._status = _IDLE
            self._start_time = None
        except StateError as ex:
            echo(
                _("Error while loading state file %s: %s. State was reset.")
                % (self._state_path, ex),
                err=True,
            )
            self._status = _IDLE
            self._start_time = None
            self._iteration = 1

    def _push_log(self) -> None:
        if self._status not in [_WORK, _PAUSE]:
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
            "iteration": self._iteration,
        }
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        with self._state_path.open("w") as state_file:
            state_file.write(json_dumps(data))
