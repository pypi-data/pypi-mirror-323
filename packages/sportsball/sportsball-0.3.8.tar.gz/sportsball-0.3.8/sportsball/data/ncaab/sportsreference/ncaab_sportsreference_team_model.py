"""NCAAB Sports Reference team model."""

# pylint: disable=too-many-arguments,too-many-locals
import datetime
import json
import urllib.parse

import extruct  # type: ignore
import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup, Tag
from w3lib.html import get_base_url

from ....cache import MEMORY
from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import TeamModel
from ...x.x_social_model import create_x_social_model
from .ncaab_sportsreference_player_model import \
    create_ncaab_sportsreference_player_model


def _create_ncaab_sportsreference_team_model(
    session: requests_cache.CachedSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
) -> TeamModel:
    response = session.get(url)
    response.raise_for_status()
    base_url = get_base_url(response.text, url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        data = extruct.extract(response.text, base_url=base_url)
        name = data["json-ld"][0]["name"]
    except json.decoder.JSONDecodeError as exc:
        h1 = soup.find("h1")
        if not isinstance(h1, Tag):
            raise ValueError("h1 is null.") from exc
        span = h1.find_all("span")
        name = span[1].get_text().strip()

    valid_player_urls = set()
    for a in soup.find_all("a"):
        player_url = urllib.parse.urljoin(url, a.get("href"))
        if player_url in player_urls:
            valid_player_urls.add(player_url)

    return TeamModel(
        identifier=name,
        name=name,
        players=[
            y
            for y in [  # pyright: ignore
                create_ncaab_sportsreference_player_model(session, x)
                for x in valid_player_urls
            ]
            if y is not None
        ],
        odds=[],
        points=points,
        ladder_rank=None,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(name, session, dt),
        field_goals=None,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_ncaab_sportsreference_team_model(
    session: requests_cache.CachedSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
) -> TeamModel:
    return _create_ncaab_sportsreference_team_model(
        session, url, dt, league, player_urls, points
    )


def create_ncaab_sportsreference_team_model(
    session: requests_cache.CachedSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
) -> TeamModel:
    """Create a team model from NCAAB Sports Reference."""
    if (
        not pytest_is_running.is_running()
        and dt < datetime.datetime.now() - datetime.timedelta(days=7)
    ):
        return _cached_create_ncaab_sportsreference_team_model(
            session, url, dt, league, player_urls, points
        )
    with session.cache_disabled():
        return _create_ncaab_sportsreference_team_model(
            session, url, dt, league, player_urls, points
        )
