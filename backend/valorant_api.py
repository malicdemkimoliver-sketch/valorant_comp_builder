"""
Client for valorant-api.com — the canonical source for the agent roster,
portraits, abilities, and map assets.

Responses are cached to data/cache/ with a TTL so the app survives offline:
memory -> fresh disk cache -> network -> stale disk cache -> None.
"""
import json
import os
import time
from typing import Optional

import requests

BASE_URL = "https://valorant-api.com/v1"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")
TTL_SECONDS = 24 * 60 * 60  # game data only changes on patches

_memory: dict = {}


def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"valorant_api_{key}.json")


def _read_cache(key: str) -> Optional[dict]:
    try:
        with open(_cache_path(key), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_cache(key: str, payload: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(key), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


def _get(key: str, path: str, params: Optional[dict] = None) -> Optional[list]:
    now = time.time()
    cached = _memory.get(key) or _read_cache(key)
    if cached and now - cached.get("fetched_at", 0) < TTL_SECONDS:
        _memory[key] = cached
        return cached["data"]
    try:
        resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        resp.raise_for_status()
        payload = {"fetched_at": now, "data": resp.json()["data"]}
        _memory[key] = payload
        _write_cache(key, payload)
        return payload["data"]
    except (requests.RequestException, KeyError, ValueError):
        if cached:  # stale data beats no data
            _memory[key] = cached
            return cached["data"]
        return None


def get_agents() -> Optional[list]:
    """Playable agents with portraits and abilities. None if API + cache unavailable."""
    raw = _get("agents", "/agents", {"isPlayableCharacter": "true"})
    if raw is None:
        return None
    return [
        {
            "uuid": a["uuid"],
            "name": a["displayName"],
            "description": a.get("description", ""),
            "role": (a.get("role") or {}).get("displayName", ""),
            "display_icon": a.get("displayIcon"),
            "full_portrait": a.get("fullPortrait"),
            "background_colors": a.get("backgroundGradientColors", []),
            "abilities": [
                {
                    "slot": ab.get("slot"),
                    "name": ab.get("displayName"),
                    "description": ab.get("description"),
                    "icon": ab.get("displayIcon"),
                }
                for ab in a.get("abilities", [])
            ],
        }
        for a in raw
    ]


def get_maps() -> Optional[list]:
    """All maps with splash art. None if API + cache unavailable."""
    raw = _get("maps", "/maps")
    if raw is None:
        return None
    return [
        {
            "uuid": m["uuid"],
            "name": m["displayName"],
            "splash": m.get("splash"),
            "list_view_icon": m.get("listViewIcon"),
            "sites": m.get("tacticalDescription"),
        }
        for m in raw
    ]
