"""
Generate data/presets.json — preset comps for the active map pool, derived
from real pick/win-rate data (data/vct_meta.json) instead of hand-curated
team comps. Rerun whenever the meta data is rescraped:

    python tools/generate_presets.py
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import meta_service                       # noqa: E402
from app.services.scoring import get_score_grade, score_comp  # noqa: E402
from backend import catalog                                 # noqa: E402

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "presets.json")
MIN_SCORE = 55  # grade B or better

# (archetype name, role counts, description)
ARCHETYPES = [
    ("Meta Standard", {"Controller": 1, "Initiator": 1, "Sentinel": 1, "Duelist": 1},
     "Highest composite-score pick in every role, plus the best remaining agent."),
    ("Double Initiator", {"Controller": 1, "Initiator": 2, "Sentinel": 1, "Duelist": 1},
     "Info-heavy executes — two initiators clear space before the duelist commits."),
    ("Double Duelist Aggression", {"Controller": 1, "Initiator": 1, "Sentinel": 1, "Duelist": 2},
     "Two opening threats for fast map control and snowball rounds."),
    ("Double Sentinel Fortress", {"Controller": 1, "Initiator": 1, "Sentinel": 2, "Duelist": 1},
     "Lockdown defense — double sentinel anchors sites and punishes flanks."),
    ("Slow Default", {"Controller": 2, "Initiator": 1, "Sentinel": 1, "Duelist": 1},
     "Utility-rich double controller comp for methodical, late-round executes."),
]


def _rated_pool(map_name: str, agents_by_name: dict) -> list[dict]:
    """S/A-tier agents on this map that we know the role of, best first."""
    groups = meta_service.get_tier_groups(map_name, include_all=False)
    pool = []
    for tier in ("S", "A"):
        for name, stats in groups.get(tier, []):
            agent = agents_by_name.get(name)
            if agent and agent.get("role"):
                pool.append(
                    {
                        **agent,
                        "tier": tier,
                        "win_rate": stats.get("win_rate"),
                        "composite": meta_service.get_composite_score(name, map_name),
                    }
                )
    pool.sort(key=lambda a: a["composite"], reverse=True)
    return pool


def _build_comp(pool: list[dict], role_counts: dict) -> list[dict] | None:
    """Fill role quotas from the pool by composite order, then the best leftover."""
    comp, used = [], set()
    for role, count in role_counts.items():
        picks = [a for a in pool if a["role"] == role][:count]
        if len(picks) < count:
            return None
        comp.extend(picks)
        used.update(a["name"] for a in picks)
    if len(comp) < 5:
        leftovers = [
            a for a in pool
            if a["name"] not in used
            # avoid a surprise 3rd duelist in non-aggression archetypes
            and not (a["role"] == "Duelist"
                     and sum(1 for c in comp if c["role"] == "Duelist") >= 2)
        ]
        if not leftovers:
            return None
        comp.append(leftovers[0])
    return comp[:5]


def generate() -> dict:
    meta = meta_service.load_meta_data()
    active_maps = meta.get("active_maps", [])
    series = meta.get("series", "ranked data")
    updated = meta.get("last_updated", date.today().isoformat())
    agents_by_name = {a["name"]: a for a in catalog.get_agents()}

    presets: dict[str, list] = {}
    for map_name in active_maps:
        pool = _rated_pool(map_name, agents_by_name)
        seen_comps = set()
        entries = []
        for arch_name, role_counts, blurb in ARCHETYPES:
            comp = _build_comp(pool, role_counts)
            if comp is None:
                continue
            names = tuple(sorted(a["name"] for a in comp))
            if names in seen_comps:
                continue
            score, _ = score_comp(comp, map_name, {})
            if score < MIN_SCORE:
                continue
            seen_comps.add(names)
            grade, _ = get_score_grade(score)
            top = max(comp, key=lambda a: a["composite"])
            entries.append(
                {
                    "name": arch_name,
                    "agents": sorted(a["name"] for a in comp),
                    "description": f"{blurb} Led by {top['name']} "
                                   f"({top['win_rate']}% WR on {map_name}).",
                    "source": f"Derived from {series} · updated {updated}",
                    "score": score,
                    "grade": grade,
                }
            )
        presets[map_name] = entries

    return {"generated": date.today().isoformat(), "series": series, "presets": presets}


if __name__ == "__main__":
    result = generate()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    total = sum(len(v) for v in result["presets"].values())
    print(f"Wrote {total} presets across {len(result['presets'])} maps -> {OUT_PATH}")
    for map_name, entries in result["presets"].items():
        print(f"  {map_name}: " + ", ".join(f"{e['name']} ({e['score']}/{e['grade']})"
                                            for e in entries))
