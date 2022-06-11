import re
from datetime import datetime
from http.client import HTTPResponse
from time import sleep
from typing import TypedDict
from urllib.request import urlopen

from bs4 import BeautifulSoup
from bs4.element import Tag
from dateparser import parse
from requests import PreparedRequest


class TagInfo(TypedDict):
    desc: str
    link: str
    name: str
    posts: int
    stamp: datetime


tag_cache: dict[str, dict[str, TagInfo]] = {}


def scrape_new_tags(site: str, fromdate: datetime, page: int = 1) -> dict[str, TagInfo]:
    """
    Scrape /tags?tab=new route of the site
    """

    if not site in tag_cache:
        tag_cache[site] = {}

    site_tags: dict[str, TagInfo] = tag_cache[site]

    next_page = True

    try:
        base = f"https://{site}/tags"

        req = PreparedRequest()
        req.prepare_url(base, {
            "tab": "new",
            "page": page
        })

        res: HTTPResponse = urlopen(req.url)
        if res.status != 200:
            print(f"failed to get /tags page")
            return site_tags

        soup = BeautifulSoup(res.read(), "html.parser")

        root = soup.find(id="tags-browser")
        if not root:
            print(f"[scraper] missing tags list")
            return site_tags

        tag: Tag
        for tag in root.select(".js-tag-cell"):
            name_tag: Tag = None
            desc_tag: Tag = None
            meta_tag: Tag = None

            children = tag.find_all("div", recursive=False)

            # thanks SE for changing the structure if tag doesn't have an excerpt
            if len(children) == 3:
                name_tag, desc_tag, meta_tag = children
            else:
                name_tag, meta_tag = children

            tag_link: Tag = name_tag.select_one(".post-tag")
            tag_name = tag_link.text.strip()

            tag_info: TagInfo = {
                "desc": "",
                "link": tag_link["href"],
                "name": tag_name,
                "posts": 0,
                "stamp": None
            }

            if meta_tag:
                posts_tag: Tag
                stamp_tag: Tag

                posts_tag, stamp_tag = meta_tag.find_all(
                    "div", recursive=False)

                stamp_text = stamp_tag.text.strip().lower().replace("created ", "")
                stamp = parse(stamp_text, settings={"TIMEZONE": "UTC"})

                # we don't care about tags that are older than fromdate
                if stamp < fromdate:
                    next_page = False
                    break

                tag_info["stamp"] = stamp
                tag_info["posts"] = int(
                    re.sub(r'^(\d+).*', r'\1', posts_tag.text)
                )

            if desc_tag:
                tag_info["desc"] = desc_tag.text.strip()

            site_tags[tag_name] = tag_info

        if next_page:
            print(f"[scraper] next tag page: {page+1}")
            sleep(2)
            site_tags |= scrape_new_tags(site, fromdate, page+1)

        return site_tags

    except Exception as e:
        print(f"[error] /tags page scrape\n{e}")
        return site_tags
