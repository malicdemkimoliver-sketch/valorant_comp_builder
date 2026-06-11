import json
import os

from fastapi import APIRouter

router = APIRouter(prefix="/api/team-comps", tags=["team-comps"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEAM_COMPS_PATH = os.path.join(BASE_DIR, "data", "team_comps.json")


@router.get("")
def list_team_comps() -> dict:
    """Curated pro-team comps per map (hand-researched, see data/team_comps.json)."""
    try:
        with open(TEAM_COMPS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"generated": None, "event_window": None, "patch": None, "comps": {}}
