"""Sports reference player model."""

import datetime
import http
from urllib.parse import unquote

import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup

from ...cache import MEMORY
from ...session import DEFAULT_TIMEOUT
from ..player_model import PlayerModel


def _fix_url(url: str) -> str:
    url = unquote(url)
    url = url.replace("Ã©", "é")
    return url


def _create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    fg: dict[str, int],
) -> PlayerModel | None:
    """Create a player model from NCAAB sports reference."""
    player_url = _fix_url(player_url)
    response = session.get(player_url, timeout=DEFAULT_TIMEOUT)
    # Some players can't be accessed on sports reference
    if response.status_code == http.HTTPStatus.FORBIDDEN:
        return None
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    h1 = soup.find("h1")
    if h1 is None:
        raise ValueError("h1 is null.")
    name = h1.get_text().strip()
    return PlayerModel(
        identifier=name,
        jersey=None,
        kicks=None,
        fumbles=None,
        fumbles_lost=None,
        field_goals=fg.get(name),
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    fg: dict[str, int],
) -> PlayerModel | None:
    return _create_sportsreference_player_model(session, player_url, fg)


def create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    dt: datetime.datetime,
    fg: dict[str, int],
) -> PlayerModel | None:
    """Create a player model from sports reference."""
    if (
        not pytest_is_running.is_running()
        and dt < datetime.datetime.now() - datetime.timedelta(days=2)
    ):
        return _cached_create_sportsreference_player_model(session, player_url, fg)
    with session.cache_disabled():
        return _create_sportsreference_player_model(session, player_url, fg)
