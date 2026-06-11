import json
import os

from fastapi import APIRouter

router = APIRouter(prefix="/api/presets", tags=["presets"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRESETS_PATH = os.path.join(BASE_DIR, "data", "presets.json")


@router.get("")
def list_presets() -> dict:
    """Data-derived preset comps per active map (see tools/generate_presets.py)."""
    try:
        with open(PRESETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"generated": None, "series": None, "presets": {}}
