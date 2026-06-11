from fastapi import APIRouter, HTTPException

from app.services import meta_service
from backend import catalog

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/{map_name}")
def map_meta(map_name: str) -> dict:
    """
    S/A/B/C tier groups for a map from the WR-centric composite score
    (win rate + normalized pick rate + good-map bonus). "NR" = agents in the
    roster with no pick/win data on this map.
    """
    maps_with_data = meta_service.get_all_maps()
    resolved = next(
        (m for m in maps_with_data if m.lower() == map_name.strip().lower()), None
    )
    if resolved is None:
        raise HTTPException(
            status_code=404,
            detail=f"No meta data for map '{map_name}'. "
            f"Maps with data: {sorted(maps_with_data)}",
        )

    meta = meta_service.load_meta_data()
    groups = meta_service.get_tier_groups(resolved, include_all=True)
    tiers = {}
    for tier, items in groups.items():
        tiers[tier] = [
            {
                "name": name,
                "win_rate": stats.get("win_rate"),
                "pick_rate": stats.get("pick_rate"),
                "composite": (
                    meta_service.get_composite_score(name, resolved)
                    if tier != "NR"
                    else None
                ),
                "on_meta": tier in ("S", "A"),
            }
            for name, stats in items
        ]

    # meta_service's NR list only covers agents.json; extend it with any
    # canonical-roster agents (e.g. brand-new releases) missing entirely.
    listed = {entry["name"] for tier_entries in tiers.values() for entry in tier_entries}
    for agent in catalog.get_agents():
        if agent["name"] not in listed:
            tiers["NR"].append(
                {
                    "name": agent["name"],
                    "win_rate": None,
                    "pick_rate": None,
                    "composite": None,
                    "on_meta": False,
                }
            )

    return {
        "map": resolved,
        "thin_data": meta_service.is_thin_map(resolved),
        "last_updated": meta.get("last_updated"),
        "series": meta.get("series"),
        "tiers": tiers,
    }
