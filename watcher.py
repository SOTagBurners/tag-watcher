from typing import Optional, TypedDict

from chatexchange.client import Client
from chatexchange.users import User


class Watcher(TypedDict):
    hours: Optional[int]
    site: str


def watch_new_tags(config: Watcher, client: Client):
    """
    Watch new tags created on the site
    """

    hours = config["hours"] or 1
    site = config["site"]

    print(f"watching tags on {site} ({hours}H interval)")
