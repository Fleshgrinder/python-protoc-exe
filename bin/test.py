#!/usr/bin/env python3
# ruff: noqa: T201
from os import environ
from pathlib import Path
import platform
from subprocess import check_call, check_output
from sys import stdout


def run(cmd: str, *args: str) -> str:
    return check_output([cmd, *args], encoding="utf8", stderr=stdout, universal_newlines=True).rstrip()


ci = environ.get("CI") == "true"
pip = ["pip", "--disable-pip-version-check", "--no-input"]
if not ci:
    pip.append("--require-virtualenv")

system = dict(Darwin="macos", Linux="linux", Windows="win")[platform.system()]
windows = system == "win"
machine = platform.machine().lower()
glob = f"*{system}*{machine}.whl"
wheel = next(map(str, Path(__file__).parent.parent.joinpath("dist").rglob(glob)), None)
if wheel is None:
    if ci:
        prefix = "::error::"
        suffix = ""
    else:
        prefix = "\033[0m\33[31m"
        suffix = "\033[0m"
    print(f"{prefix}Could not find any wheels in dist for glob {glob!r}.{suffix}")
    raise SystemExit(1)

check_call([*pip, "install", "--force-reinstall", wheel])

results = [
    run("where" if windows else "which", "protoc"),
    run("protoc", "--version"),
]

if ci:
    prefix = "::notice::"
    infix = "%0A"
    suffix = ""
else:
    prefix = "\033[0m\033[32m"
    infix = "\n"
    suffix = "\033[0m"
    check_call([*pip, "uninstall", "--yes", wheel])

print(f"{prefix}{infix.join(results)}{suffix}")
