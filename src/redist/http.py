from os import environ
from typing import Final

from requests import Session

ACCEPT_JSON: Final = dict(Accept="application/json")
ACCEPT_BINARY: Final = dict(Accept="application/octet-stream")
SESSION: Final = Session()


token = environ.get("GITHUB_TOKEN", environ.get("GH_TOKEN", ""))
if token.startswith("ghp_"):
    SESSION.headers["Authorization"] = f"Bearer {token}"
del token
