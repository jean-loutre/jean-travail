from configparser import ConfigParser
from functools import wraps
from gettext import gettext as _
from pathlib import Path
from typing import Any, Callable

from appdirs import user_config_dir
from click import Command, Context, Option
from click import Path as ClickPath
from click import echo, group, option, pass_context, pass_obj
from click.core import ParameterSource  # type: ignore

from jtravail.pomodoro import Pomodoro

_APP_NAME = "jean-travail"
_APP_AUTHOR = "ottorg"
DEFAULT_CONFIG_FILE = Path(user_config_dir(_APP_NAME, _APP_AUTHOR)) / "config.cfg"


class ConfigOption(Option):
    pass


class ConfigCommand(Command):
    def invoke(self, context: Context) -> Any:
        config_file_path = context.params.get("config", DEFAULT_CONFIG_FILE)
        config = ConfigParser()
        config.read(config_file_path)
        for parameter in self.params:
            if not isinstance(parameter, ConfigOption):
                continue

            name = parameter.name

            if context.get_parameter_source(name) != ParameterSource.DEFAULT:  # type: ignore
                continue

            config_value = config.get("options", name, fallback=None)
            if config_value is None:
                continue

            context.params[name] = parameter.type(config_value)

        return super().invoke(context)


def print_status(
    command: Callable[[Pomodoro], None]
) -> Callable[[Pomodoro, int, int], None]:
    @wraps(command)
    @option(
        "-w",
        "--work-duration",
        cls=ConfigOption,
        type=int,
        default=25,
        envvar="JTRAVAIL_WORK_DURATION",
        help=_("Work session duration in minutes"),
        show_default=True,
    )
    @option(
        "-p",
        "--pause-duration",
        cls=ConfigOption,
        type=int,
        default=5,
        envvar="JTRAVAIL_PAUSE_DURATION",
        help=_("Pause session duration in minutes"),
        show_default=True,
    )
    def _wrapper(
        pomodoro: Pomodoro,
        work_duration: int,
        pause_duration: int,
    ) -> None:
        command(pomodoro)
        if pomodoro.stopped:
            status_name = _("Stopped")
        elif pomodoro.working:
            status_name = _("Working")
        elif pomodoro.paused:
            status_name = _("Paused")

        remaining_time = pomodoro.get_remaining_time(
            work_duration=work_duration, pause_duration=pause_duration
        )
        minutes = int(remaining_time.total_seconds() / 60)
        seconds = abs(int(remaining_time.total_seconds() - 60 * minutes))
        echo(
            _("{status}: {minutes:02d}:{seconds:02d}").format(
                status=status_name, minutes=minutes, seconds=seconds
            )
        )

    return _wrapper


@group()
@pass_context
@option(
    "-c",
    "--config",
    type=ClickPath(dir_okay=False, exists=True),
    show_default=str(DEFAULT_CONFIG_FILE),
    help=_("Path to configuration file"),
)
def main(context: Context, config: Path | None = None) -> None:
    context.obj = Pomodoro(config_path=config)


@main.command(cls=ConfigCommand)
@pass_obj
@print_status
def next(pomodoro: Pomodoro) -> None:
    pomodoro.next()


@main.command(cls=ConfigCommand)
@pass_obj
@print_status
def status(pomodoro: Pomodoro) -> None:
    pass


@main.command()
@pass_obj
@print_status
def stop(pomodoro: Pomodoro) -> None:
    pomodoro.stop()
