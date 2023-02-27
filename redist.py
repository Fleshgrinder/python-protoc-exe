#!/usr/bin/env python3
import os
import platform
import shutil
from copy import deepcopy
from email.message import EmailMessage
from pathlib import Path
from subprocess import DEVNULL, STDOUT, check_call, check_output
from tempfile import mkdtemp
from time import gmtime, strftime
from typing import Any, Final, Literal, NoReturn, TypeAlias, final
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import click
from click_help_colors import HelpColorsGroup
from packaging.version import Version
from rich import markup, traceback
from rich.console import Console
from wheel.wheelfile import WheelFile

# region ----------------------------------------------------------------------- paths
ROOT_DIR: Final = Path(__file__).parent.absolute()
CACHE_DIR: Final = ROOT_DIR / ".cache"
BUILD_DIR: Final = ROOT_DIR / "build"
DIST_DIR: Final = ROOT_DIR / "dist"
# endregion -------------------------------------------------------------------- paths
# region ----------------------------------------------------------------------- config
EXE_NAME: Final = "protoc"
EXE_TEST_ARGS: Final = ("--version",)

PRJ_NAME: Final = f"{EXE_NAME}-exe"
PRJ_DESC_PATH: Final = ROOT_DIR / "README.md"

ORIGIN: Final = f"fleshgrinder/python-{PRJ_NAME}"
ORIGIN_URL: Final = f"https://github.com/{ORIGIN}"

UPSTREAM: Final = "protocolbuffers/protobuf"
UPSTREAM_URL: Final = f"https://github.com/{UPSTREAM}"

PYPI_METADATA: Final = {
    "Metadata-Version": "2.1",
    "Name": PRJ_NAME,
    "Summary": "PyPI packaged Protocol Buffers Compiler",
    "Description-Content-Type": "text/markdown",
    "Author": "Google",
    "Maintainer": "Fleshgrinder",
    "Maintainer-email": "pypi@fleshgrinder.com",
    "Home-page": ORIGIN_URL,
    "License-File": "LICENSE",
    "License": "BSD-3-Clause",
    "Classifier": [
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    "Project-URL": [
        "Official Website, https://protobuf.dev/",
        f"Source Code, {UPSTREAM_URL}",
        f"Issue Tracker, {UPSTREAM_URL}/issues",
    ],
}

WHL_NAME: Final = PRJ_NAME.replace("-", "_")
WHL_METADATA: Final = {
    "Wheel-Version": "1.0",
    "Generator": ORIGIN_URL,
    "Root-Is-Purelib": "false",
}

EXE_CACHE_DIR: Final = CACHE_DIR / EXE_NAME
EXE_BUILD_DIR: Final = BUILD_DIR / EXE_NAME
# endregion -------------------------------------------------------------------- config
# region ----------------------------------------------------------------------- utils
CI: Final = "CI" in os.environ
GHA: Final = "GITHUB_ACTIONS" in os.environ
CONSOLE: Final = Console(stderr=True)
VERBOSE = False

# region ----------------------------------------------------------------------- style
traceback.install(console=CONSOLE, show_locals=True)

Severity: TypeAlias = Literal["debug", "notice", "warning", "error"]

if GHA:

    def log(s: Severity, m: Any) -> None:
        m = m.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
        CONSOLE.print(f"::{s}::{m}")

else:
    _LOG_COLORS: Final = dict[Severity, str](debug="bright_black", notice="blue", warning="yellow", error="red")

    def log(s: Severity, m: Any) -> None:
        CONSOLE.print(f"[{_LOG_COLORS[s]}][bold]{s.upper()}:[/bold] {m}")


def debug(m: Any) -> None:
    if CI or VERBOSE:
        log("debug", m)


def info(m: Any) -> None:
    CONSOLE.print(m)


def notice(m: Any) -> None:
    log("notice", m)


def warning(m: Any) -> None:
    log("warning", m)


def error(m: Any) -> None:
    log("error", m)


def done(m: Any) -> NoReturn:
    info(m)
    raise SystemExit(0)


def fail(m: Any, ec: int = 1) -> NoReturn:
    error(m)
    raise SystemExit(ec)


# endregion -------------------------------------------------------------------- style


# noinspection SpellCheckingInspection
def map_platform(s: str) -> str | None:
    s = s.removesuffix(".zip")
    s = s.removeprefix(f"{EXE_NAME}-")
    s = s[s.index("-") + 1 :]
    return {
        "linux-aarch_64": "manylinux_2_17_aarch64.manylinux2014_aarch64",
        "linux-ppcle_64": "manylinux_2_17_ppc64le.manylinux2014_ppc64le",
        "linux-s390_64": "manylinux_2_17_s390x.manylinux2014_s390x",
        "linux-x86_32": "manylinux_2_5_i686.manylinux1_i686",
        "linux-x86_64": "manylinux_2_5_x86_64.manylinux1_x86_64",
        "osx-aarch_64": "macosx_11_0_arm64",
        "osx-x86_64": "macosx_10_4_x86_64",
        "win32": "win32",
        "win64": "win_amd64",
    }.get(s)


def run(cmd: str, *args: str, stderr: int | None = None) -> str:
    return check_output(
        (cmd, *args),
        encoding="utf8",
        stderr=stderr,
        universal_newlines=True,
    ).rstrip()


def has_uncommitted_changes() -> bool:
    return run("git", "status", "--porcelain=v1", stderr=DEVNULL) != ""


@final
class ReproducibleWheelFile(WheelFile):
    def writestr(self, zi: ZipInfo, *args, **kwargs) -> None:
        zi.create_system = 3
        zi.date_time = (1980, 1, 1, 0, 0, 0)
        super().writestr(zi, *args, **kwargs)


def emsg(headers: dict[str, Any], payload: str | None = None) -> bytes:
    em = EmailMessage()
    for hk, hv in headers.items():
        if isinstance(hv, list):
            for e in hv:
                em[hk] = e
        else:
            em[hk] = hv
    if payload:
        em.set_payload(payload)
    return bytes(em)


def maybe_clean(clean: bool, directory: Path) -> None:  # noqa: FBT001
    if clean is True and directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


# endregion -------------------------------------------------------------------- utils
# region ----------------------------------------------------------------------- cli
@click.group(
    cls=HelpColorsGroup,
    context_settings={"help_option_names": ("-h", "--help")},
    help_headers_color="yellow",
    help_options_color="green",
)
@click.option("--verbose", is_flag=True)
def redist(*, verbose: bool) -> None:
    global VERBOSE  # noqa: PLW0603
    VERBOSE = verbose


@redist.command()
@click.option("-c", "--clean", is_flag=True)
@click.argument("version", default="latest")
def download(version: str, *, clean: bool) -> None:
    maybe_clean(clean, EXE_CACHE_DIR)

    check_call(["bash", str(ROOT_DIR / "bin/download"), version])


@redist.command()
@click.option("-c", "--clean", is_flag=True)
@click.option("-t", "--tag", "tag_glob", default="*", metavar="glob")
def build(*, clean: bool, tag_glob: str) -> None:
    maybe_clean(clean, EXE_BUILD_DIR)

    for src in EXE_CACHE_DIR.glob(tag_glob):
        if not src.is_dir():
            debug(f"ignoring non-directory: {src.relative_to(ROOT_DIR)}")
            continue

        dst = EXE_BUILD_DIR / src.name
        try:
            dst.mkdir(parents=True)
        except FileExistsError:
            debug(f"ignoring existing: {dst.relative_to(ROOT_DIR)}")
            continue

        shutil.copyfile(src / "LICENSE", dst / "LICENSE")

        for exe_src in src.glob("*.zip"):
            if not exe_src.is_file():
                debug(f"ignoring non-file: {exe_src.relative_to(ROOT_DIR)}")
                continue

            exe_platform = map_platform(exe_src.name)
            if exe_platform is None:
                warning(f"Unknown platform [bold]{markup.escape(exe_src.name)}[/bold]")
                continue
            exe_platform = f"py2.py3-none-{exe_platform}"

            zip_file = ZipFile(exe_src)
            for it in zip_file.namelist():
                if it in ("bin/protoc", "bin/protoc.exe"):
                    with dst.joinpath(exe_platform).open("wb") as fp:
                        fp.write(zip_file.read(it))
                    break


@redist.command()
@click.option("-c", "--clean", is_flag=True)
@click.option("-d", "--dev", is_flag=True)
@click.option("-t", "--tag", default="*")
def assemble(*, clean: bool, dev: bool, tag: str) -> None:
    maybe_clean(clean, DIST_DIR)

    if dev is True:
        dt = strftime("%Y%m%d%H%M%S", gmtime(int(run("git", "log", "-1", "--format=%ct"))))
        version_suffix = f".dev{dt}"
    else:
        version_suffix = ""

    description = PRJ_DESC_PATH.read_text()
    pypi_metadata = deepcopy(PYPI_METADATA)
    whl_metadata = deepcopy(WHL_METADATA)

    for tag_dir in EXE_BUILD_DIR.glob(tag):
        if not tag_dir.is_dir():
            debug(f"ignoring non-dir: {tag_dir.relative_to(ROOT_DIR)}")
            continue

        tag = tag_dir.name
        version = str(Version(f"{tag.removeprefix('v')}{version_suffix}"))
        whl_name = f"{WHL_NAME}-{version}"
        pypi_metadata["Version"] = version
        pypi_metadata["Download-URL"] = f"{UPSTREAM_URL}/releases/tag/{tag}"
        license_ = (tag_dir / "LICENSE").read_bytes()
        for exe_file in tag_dir.glob("py2.py3-none-*"):
            if not exe_file.is_file():
                debug(f"ignoring non-file: {exe_file.relative_to(ROOT_DIR)}")
                continue

            pypi_platform = exe_file.name
            whl_file = DIST_DIR / f"{whl_name}-{pypi_platform}.whl"
            if whl_file.exists():
                debug(f"skipping existing wheel: {whl_file.relative_to(ROOT_DIR)}")
                continue

            whl_metadata["Tag"] = pypi_platform
            exe_name = f"{EXE_NAME}.exe" if pypi_platform.startswith("py2.py3-none-win") else EXE_NAME
            dist_info = f"{whl_name}.dist-info"
            with ReproducibleWheelFile(whl_file, "w") as it:
                for _k, v, p in (
                    (f"{whl_name}.data/scripts/{exe_name}", exe_file.read_bytes(), 0o755),
                    (f"{dist_info}/LICENSE", license_, 0o644),
                    (f"{dist_info}/METADATA", emsg(pypi_metadata, description), 0o644),
                    (f"{dist_info}/WHEEL", emsg(whl_metadata), 0o644),
                ):
                    k = ZipInfo(_k)
                    k.compress_type = ZIP_DEFLATED
                    k.external_attr = (p + 0o100000) << 16
                    k.file_size = len(v)
                    it.writestr(k, v)


@redist.command()
@click.option("-v", "--version", default="*")
def verify(*, version: str) -> None:
    from twine.commands.check import check

    os.chdir(DIST_DIR)
    dists = [str(it.relative_to(DIST_DIR)) for it in DIST_DIR.glob(f"{WHL_NAME}-{version}-*.whl") if it.is_file()]
    if check(dists, strict=True):
        raise SystemExit(1)


@redist.command()
@click.option("-v", "--version", default="*")
@click.argument("args", nargs=-1)
def test(args: tuple[str, ...], *, version: str) -> None:
    if len(args) == 0:
        args = EXE_TEST_ARGS

    system = {"Darwin": "macos", "Linux": "linux", "Windows": "win"}[platform.system()]
    windows = system == "win"
    machine = platform.machine()
    machine = f"_{machine.lower()}" if windows else f"*{machine}"
    glob = f"{WHL_NAME}-{version}-*-{system}{machine}.whl"
    wheel = next(map(str, DIST_DIR.glob(glob)), None)
    if wheel is None:
        fail(f"Could not find any wheel matching [bold]{glob!r}[/bold] in {DIST_DIR.relative_to(ROOT_DIR)}")

    tmp = None
    pip = ["pip", "--disable-pip-version-check", "--no-input"]
    if not CI:
        tmp = mkdtemp(dir=BUILD_DIR)
        os.chdir(tmp)
        pip.append("--require-virtualenv")
    try:
        check_call([*pip, "install", "--force-reinstall", wheel])

        results = (
            run("where" if windows else "which", EXE_NAME, stderr=STDOUT),
            run(EXE_NAME, *args, stderr=STDOUT),
        )
        notice("\n".join(results))

        if not CI:
            check_call([*pip, "uninstall", "--yes", wheel])
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)


@redist.command()
@click.option("-f", "--force", is_flag=True)
@click.option("-v", "--version", default="*")
@click.argument("repo", default="testpypi")
def publish(repo: str, *, force: bool, version: str) -> None:
    """Publish all wheels from the distribution directory to the given repo."""
    if force is False and has_uncommitted_changes() is True:
        fail("Refusing publication, you have uncommitted changes, use [bold]--force[/bold] to ignore this check.")

    from twine.commands.upload import upload
    from twine.settings import Settings

    settings = Settings(repository_name=repo)
    for version_dir in DIST_DIR.glob(version):
        if version_dir.is_dir():
            upload(settings, [str(it) for it in version_dir.glob("*.whl") if it.is_file()])


# endregion -------------------------------------------------------------------- cli
if __name__ == "__main__":
    redist()
