"""
Meta Service V3 — profile-aware agent tiers.

WHAT CHANGED:
  Old logic: "On Meta" = |WR - PR| < 15%  (volatile — a tiny stat shift
  flipped an agent between Meta and Off).
  New logic: a COMPOSITE SCORE blending three stable signals:
      composite = win_rate * 0.50  +  pick_rate * 0.35  +  map_profile_bonus
  where map_profile_bonus = +6 if the map is in the agent's good_maps
  (from agents.json), else 0.

  Tiers from composite:
      S  >= 60   (pro-meta essential on this map)
      A  >= 48   (strong meta pick)
      B  >= 38   (viable)
      C  <  38   (niche)

All V2 function names are kept so existing imports don't break.
"""
import json
import os
from typing import Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

_meta_cache: Optional[Dict] = None
_profile_cache: Optional[Dict[str, dict]] = None

# Composite weights and tier thresholds.
# Pick rate is NORMALIZED to the highest pick rate on each map, which makes
# tiers scale-invariant: works for pro data (top PR ~95%) and ranked data
# from vstats.gg (top PR ~15%) without retuning.
WR_WEIGHT = 1.0           # win rate is the primary signal (ranked data)
PR_NORM_WEIGHT = 8.0      # small popularity nudge (PR is compressed in ranked)
GOOD_MAP_BONUS = 3.0
# Thresholds on the WR-centric composite (WR + up to 8 PR-norm + 3 good-map):
TIER_THRESHOLDS = [("S", 56), ("A", 52), ("B", 49)]  # below last = "C"


# ── Loading ───────────────────────────────────────────────────────────────────
def load_meta_data() -> Dict:
    """Load vct_meta.json (cached)."""
    global _meta_cache
    if _meta_cache is None:
        path = os.path.join(DATA_DIR, "vct_meta.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                _meta_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _meta_cache = {}
    return _meta_cache


def _load_agent_profiles() -> Dict[str, dict]:
    """Load agents.json directly for good_maps lookups (cached)."""
    global _profile_cache
    if _profile_cache is None:
        path = os.path.join(DATA_DIR, "agents.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            _profile_cache = {a.get("name", ""): a for a in raw}
        except (FileNotFoundError, json.JSONDecodeError):
            _profile_cache = {}
    return _profile_cache


def is_meta_loaded() -> bool:
    return bool(_get_meta_by_map())


KNOWN_MAPS = {"Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox",
              "Lotus", "Pearl", "Split", "Abyss", "Sunset", "Corrode"}


def _get_meta_by_map() -> Dict:
    """
    Normalize either supported structure of vct_meta.json:
      A) {"meta_by_map": {"Ascent": {...}, ...}, "last_updated": ...}
      B) {"Ascent": {...}, "Bind": {...}, ...}   (maps at top level)
    Returns the {map: {agent: stats}} dict in both cases.
    """
    meta = load_meta_data()
    if not meta:
        return {}
    if "meta_by_map" in meta and isinstance(meta["meta_by_map"], dict):
        return meta["meta_by_map"]
    # Structure B: top-level keys that are map names mapping to agent dicts
    by_map = {k: v for k, v in meta.items()
              if isinstance(v, dict) and (k in KNOWN_MAPS or
                  any(isinstance(s, dict) and ("win_rate" in s or "pick_rate" in s)
                      for s in v.values()))}
    return by_map


# ── Core accessors (names kept from V2) ──────────────────────────────────────
def get_all_maps() -> List[str]:
    return list(_get_meta_by_map().keys())


def get_all_meta_agents_for_map(map_name: str) -> Dict[str, dict]:
    return _get_meta_by_map().get(map_name, {})


def get_agent_meta_for_map(agent_name: str, map_name: str) -> Optional[dict]:
    return get_all_meta_agents_for_map(map_name).get(agent_name)


def get_map_agent_list(map_name: str) -> List[Tuple[str, dict]]:
    """Agents on a map sorted by composite score (best first)."""
    agents = get_all_meta_agents_for_map(map_name)
    scored = [(name, stats, get_composite_score(name, map_name))
              for name, stats in agents.items()]
    scored.sort(key=lambda x: x[2], reverse=True)
    return [(name, stats) for name, stats, _ in scored]


def get_best_agents_for_map(map_name: str, limit: int = 5) -> List[Tuple[str, dict]]:
    return get_map_agent_list(map_name)[:limit]


def get_all_agents_across_maps() -> List[str]:
    names = set()
    for agents in _get_meta_by_map().values():
        names.update(agents.keys())
    return sorted(names)


# ── V3 composite tier logic ──────────────────────────────────────────────────
def _max_pick_rate(map_name: str) -> float:
    """Highest pick rate on a map — used to normalize PR across data scales."""
    agents = get_all_meta_agents_for_map(map_name)
    prs = [float(s.get("pick_rate", 0)) for s in agents.values()]
    return max(prs) if prs else 1.0


def get_composite_score(agent_name: str, map_name: str) -> float:
    """
    Composite meta score for an agent on a map.
    Blends win rate (stability), pick rate normalized to the map's top pick
    (popularity relative to peers), and the agent's own map profile.
    """
    stats = get_agent_meta_for_map(agent_name, map_name)
    if not stats:
        return 0.0
    wr = float(stats.get("win_rate", 0))
    pr = float(stats.get("pick_rate", 0))
    max_pr = _max_pick_rate(map_name)
    pr_norm = (pr / max_pr) if max_pr > 0 else 0.0   # 0..1 relative to top pick

    score = wr * WR_WEIGHT + pr_norm * PR_NORM_WEIGHT

    profile = _load_agent_profiles().get(agent_name)
    if profile and map_name in profile.get("good_maps", []):
        score += GOOD_MAP_BONUS
    return round(score, 1)


def get_agent_tier(agent_name: str, map_name: str) -> Optional[str]:
    """Return S/A/B/C tier from composite score, or None if no data."""
    stats = get_agent_meta_for_map(agent_name, map_name)
    if not stats:
        return None
    score = get_composite_score(agent_name, map_name)
    for tier, threshold in TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return "C"


def get_agent_meta_tier(agent_name: str, map_name: str) -> Optional[str]:
    """Alias kept for backward compatibility."""
    return get_agent_tier(agent_name, map_name)


def is_on_meta(agent_name: str, map_name: str) -> bool:
    """An agent is 'on meta' if it lands S or A tier on this map."""
    return get_agent_tier(agent_name, map_name) in ("S", "A")


def get_meta_status(agent_name: str, map_name: str) -> Tuple[bool, float, str]:
    """
    Returns (is_meta, composite_score, explanation).
    Kept for backward compatibility with V2 callers.
    """
    stats = get_agent_meta_for_map(agent_name, map_name)
    if not stats:
        return False, 0.0, "No meta data for this agent on this map."

    score = get_composite_score(agent_name, map_name)
    tier = get_agent_tier(agent_name, map_name)
    wr = stats.get("win_rate", 0)
    pr = stats.get("pick_rate", 0)

    profile = _load_agent_profiles().get(agent_name, {})
    map_fit = "strong map for this agent" if map_name in profile.get("good_maps", []) \
              else "not a signature map"

    if tier == "S":
        expl = f"S Tier — {wr}% WR, {pr}% PR, {map_fit}. Pro-meta essential."
    elif tier == "A":
        expl = f"A Tier — {wr}% WR, {pr}% PR, {map_fit}. Strong meta pick."
    elif tier == "B":
        expl = f"B Tier — {wr}% WR, {pr}% PR, {map_fit}. Viable choice."
    else:
        expl = f"C Tier — {wr}% WR, {pr}% PR, {map_fit}. Niche pick."

    return tier in ("S", "A"), score, expl


def get_tier_groups(map_name: str) -> Dict[str, List[Tuple[str, dict]]]:
    """
    All agents on a map grouped by tier: {"S": [(name, stats), ...], ...}
    Each tier list is sorted by composite score descending.
    Used by the Meta Tracker tier list.
    """
    groups: Dict[str, List[Tuple[str, dict, float]]] = {"S": [], "A": [], "B": [], "C": []}
    for name, stats in get_all_meta_agents_for_map(map_name).items():
        tier = get_agent_tier(name, map_name) or "C"
        groups[tier].append((name, stats, get_composite_score(name, map_name)))
    out: Dict[str, List[Tuple[str, dict]]] = {}
    for tier, items in groups.items():
        items.sort(key=lambda x: x[2], reverse=True)
        out[tier] = [(n, s) for n, s, _ in items]
    return out
