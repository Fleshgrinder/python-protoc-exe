from __future__ import annotations
from os import environ
from typing import Final, TypeAlias, Literal, Any

from rich.console import Console

LogLevel: TypeAlias = Literal["debug", "notice", "warning", "error"]

CONSOLE: Final = Console(stderr=True)

if "GITHUB_ACTIONS" in environ:
    def log(level: LogLevel, message: Any) -> None:
        message = str(message).replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")  # TODO
        CONSOLE.print(f"::{level}::{message}")
else:
    LOG_COLORS: Final = dict(debug="bright black", notice="blue", warning="yellow", error="red")


    def log(level: LogLevel, message: Any) -> None:
        CONSOLE.print(f"[{LOG_COLORS[level]}]{message}")


def debug(message: Any) -> None:
    log("debug", message)


def info(message: Any) -> None:
    CONSOLE.print(message)


def notice(message: Any) -> None:
    log("notice", message)


def warning(message: Any) -> None:
    log("warning", message)


def error(message: Any) -> None:
    log("error", message)
