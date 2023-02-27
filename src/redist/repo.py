from abc import ABC
from re import Pattern
from typing import final, Final, Iterable

from redist.http import SESSION, ACCEPT_JSON
from redist.json import JSON_PARSER
from redist.release import Release


class Repo(ABC):
    pass


class SrcRepo(Repo, ABC):
    pass


class DstRepo(Repo, ABC):
    pass


class GHRepo(Repo, ABC):
    __slots__ = ("__repo", "__base_url")

    def __init__(self, repo: str, *, base_url: str | None = None) -> None:
        self.__repo: Final = repo
        self.__base_url: Final = "https://api.github.com" if base_url is None else base_url.rstrip("/")

    def releases(self) -> Iterable[Release]:
        url = f"{self.__base_url}/repos/{self.__repo}/releases?per_page=100"
        while True:
            response = SESSION.get(url, headers=ACCEPT_JSON)
            response.raise_for_status()
            yield from map(Release, JSON_PARSER.parse(response.content, recursive=True))
            if "next" not in response.links:
                break
            url = response.links["next"]["url"]


@final
class GHSrcRepo(GHRepo, SrcRepo):
    def releases(self, tag_filter: Pattern | None = None, *ignore: Release) -> Iterable[Release]:
        if tag_filter is None:
            if ignore is None:
                return super().releases()
            return (it for it in super().releases() if it not in ignore)
        elif ignore is None:
            return (it for it in super().releases() if tag_filter.match(it.tag))
        return (it for it in super().releases() if it not in ignore and tag_filter.match(it.tag))


@final
class GHDstRepo(GHRepo, DstRepo):
    pass
