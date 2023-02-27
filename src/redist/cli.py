import re
from re import Pattern
from typing import Collection

import click

from redist.console import notice, warning, CONSOLE
from redist.repo import GHSrcRepo, GHDstRepo


# redist
#   --src-repo      github:protocolbuffers/protobuf
#   --dst-repo      github:fleshgrinder/python-protoc-exe
#   --tag-filter    '\Av(?:3\.\d+|[2-9]\d+)\.\d+\Z'
#   --asset-filter  '\Aprotoc-\d.*?-(?:linux|osx|win).*?\.zip\Z'
#   --exe-name      protoc
#   --archive-path  bin/protoc bin/protoc.exe
#   --project-name  protoc-exe
@click.command()
@click.option("--src-repo", required=True)
@click.option("--dst-repo", required=True)
@click.option("--tag-filter", type=re.compile)
@click.option("--asset-filter", type=re.compile)
@click.option("--exe-name")
@click.option("--archive-path")  # TODO nargs
@click.option("--project-name")  # TODO f"{exe_name}-exe"
@click.option("--publish", is_flag=True)
@click.option("--repo", default="testpypi")
def cli(
    src_repo: str,
    dst_repo: str,
    tag_filter: Pattern | None,
    asset_filter: Pattern | None,
    exe_name: str | None,
    archive_paths: Collection[str] | None,
    project_name: str | None,
    publish: bool,
    repo: str,
) -> None:
    with CONSOLE.status(""):
        src = GHSrcRepo(src_repo)
        dst = GHDstRepo(dst_repo)
        for release in src.releases(tag_filter, *dst.releases()):
            notice(release)
            for asset in release.assets(asset_filter):
                warning(asset)
