from typing import Any
from typing import Optional
from urllib.parse import urlencode

import httpx

from league_client.constants import HEADERS
from league_client.types import ProxyT


def get_match_data(
    access_token: str,
    puuid: str,
    player_platform_edge_url: str,
    proxy: Optional[ProxyT] = None,
    count: int = 30,
    queue_id: int = -1,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {access_token}"
    query = {
        "startIndex": 0,
        "count": count,
        "tagsQueryType": "AND",
    }
    if queue_id != -1:
        query["tag"] = f"q_{queue_id}"
    res = httpx.get(
        (
            f"{player_platform_edge_url}/match-history-query/v1/products"
            f"/lol/player/{puuid}/SUMMARY?" + urlencode(query)
        ),
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def get_flash_key(
    match_data: dict[str, Any],
    summoner_id: int,
) -> str | None:
    # returns "D" or "F" or None
    try:
        participants = match_data["games"][0]["json"]["participants"]
    except (KeyError, IndexError, TypeError):
        return None

    for player in participants:
        if player.get("summonerId") == summoner_id:
            if player.get("spell1Id") == 4:
                return "D"
            elif player.get("spell2Id") == 4:
                return "F"
    return None
