from __future__ import annotations

from re import Pattern
from typing import Mapping, Any, Final, final, Iterable


@final
class Asset:
    __slots__ = ("__data", "__name", "__release")

    def __init__(self, data: Mapping[str, Any], release: Release) -> None:
        self.__data: Final = data
        self.__name: Final[str] = data["name"]
        self.__release: Final = release

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Asset) and self.__name == other.__name and self.__release == other.__release

    def __hash__(self) -> int:
        return hash(self.__name)

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(data={self.__data!r}, release={self.__release!r})"

    @property
    def name(self) -> str:
        return self.__name

    def download(self) -> bytes:
        pass


@final
class Release:
    __slots__ = ("__data", "__tag")

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.__data: Final = data
        self.__tag: Final[str] = data["tag_name"]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Release) and self.__tag == other.__tag

    def __hash__(self) -> int:
        return hash(self.__tag)

    def __str__(self) -> str:
        return self.__tag

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(data={self.__data!r})"

    def assets(self, asset_filter: Pattern | None = None) -> Iterable[Asset]:
        assets = (Asset(it, self) for it in self.__data["assets"])
        if asset_filter is None:
            return assets
        return (it for it in assets if asset_filter.match(it.name))

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def version(self) -> str:
        return self.__tag.removeprefix("v")
