"""
Background refresh of the meta stats: scrape MetaBot -> rewrite
data/vct_meta.json -> clear meta_service caches -> regenerate presets.
One refresh at a time; status readable via GET /api/meta/status.
"""
import json
import os
import threading
from datetime import date, datetime, timezone
from typing import Optional

from app.services import meta_scraper, meta_service

_lock = threading.Lock()
_state = {
    "running": False,
    "started_at": None,
    "finished_at": None,
    "last_result": None,
    "last_error": None,
}

PRESETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "presets.json"
)


def _regenerate_presets() -> None:
    # Local import: tools/ is only needed here, and only after fresh data exists
    from tools.generate_presets import generate

    result = generate()
    with open(PRESETS_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def _run() -> None:
    try:
        summary = meta_scraper.refresh_meta()
        if summary["written"]:
            meta_service.clear_cache()
            _regenerate_presets()
        with _lock:
            _state["last_result"] = summary
            _state["last_error"] = None
    except Exception as exc:  # surfaced via /api/meta/status, not crash the app
        with _lock:
            _state["last_error"] = str(exc)
    finally:
        with _lock:
            _state["running"] = False
            _state["finished_at"] = datetime.now(timezone.utc).isoformat()


def start_refresh() -> bool:
    """Kick a background refresh. Returns False if one is already running."""
    with _lock:
        if _state["running"]:
            return False
        _state["running"] = True
        _state["started_at"] = datetime.now(timezone.utc).isoformat()
    threading.Thread(target=_run, daemon=True).start()
    return True


def status() -> dict:
    meta = meta_service.load_meta_data()
    with _lock:
        snapshot = dict(_state)
    return {
        **snapshot,
        "last_updated": meta.get("last_updated"),
        "series": meta.get("series"),
        "stale": is_stale(),
    }


def is_stale() -> bool:
    """Data is stale once last_updated is before today."""
    meta = meta_service.load_meta_data()
    last = meta.get("last_updated")
    if not last:
        return True
    try:
        return date.fromisoformat(last) < date.today()
    except ValueError:
        return True


def refresh_if_stale() -> Optional[bool]:
    """Startup hook: refresh in the background when the data is outdated."""
    if is_stale():
        return start_refresh()
    return None
