"""
Scoring engine V3 — gentler, simpler, fairer.

WHY V3:
  V2 relied on many fine-grained tags; if an agent's data was thin, combos
  silently never fired and good comps scored under 50. V3 fixes that:

  1. ROLE FALLBACKS — if an agent's utility/tag data is missing or thin,
     sensible defaults are inferred from its role (every Controller smokes,
     every Initiator brings info, every Sentinel anchors, every Duelist
     entries). Scores no longer collapse on incomplete data.
  2. FEWER COMPONENTS — 5 instead of 7.
  3. SOFTER PENALTIES — and total penalties are capped at -20.

Breakdown (totals 100):
  Role Balance     (30): the single most important thing in a comp
  Map Fit          (20): good_maps match OR S/A meta tier on the map
  Utility Coverage (20): smokes, recon, flash, post-plant
  Synergy          (15): complementary combos (entry+flash, smokes+entry...)
  Meta Alignment   (15): per-agent meta tier on the selected map

Expected ranges: meta comps 85-95 · solid comps 70-84 · flawed 50-69 · bad <50
"""
from typing import List, Dict, Tuple

try:
    from app.services.meta_service import get_agent_tier, is_meta_loaded
    _META_AVAILABLE = True
except Exception:
    _META_AVAILABLE = False


# ── Tag/utility groups ────────────────────────────────────────────────────────
RECON_UTIL = {"recon-bolt", "drone", "haunt", "camera", "tripwire", "trademark",
              "prowler", "trailblazer", "sonic-sensor", "alarmbot", "recon"}
FLASH_UTIL = {"flash", "paranoia", "blind"}
POST_PLANT_UTIL = {"nanoswarm", "snake-bite", "shock-dart", "orbital", "molotov",
                   "grenades", "razorvine", "guided-salvo", "post-plant"}
VISION_BLOCK = {"smokes", "wall", "orb", "cove", "cascade"}
ANCHOR_TAGS = {"anchor", "site-control"}
FLANK_TAGS = {"flank-control"}
ZONE_TAGS = {"defensive", "zone-control"}

# Role fallbacks — what every agent of a role inherently provides
ROLE_DEFAULT_UTIL = {
    "Controller": {"smokes"},
    "Initiator": {"recon", "flash"},
    "Sentinel": {"tripwire"},
    "Duelist": set(),
}
ROLE_DEFAULT_TAGS = {
    "Controller": {"smokes"},
    "Initiator": {"information"},
    "Sentinel": {"anchor", "flank-control"},
    "Duelist": {"entry", "aggressive"},
}


def _attr(agent, name, default=None):
    """Duck-typed attribute access — works with any Agent class or dict."""
    if isinstance(agent, dict):
        return agent.get(name, default if default is not None else [])
    return getattr(agent, name, default if default is not None else [])


def _fits_map(agent, map_name: str) -> bool:
    fits = getattr(agent, "fits_map", None)
    if callable(fits):
        try:
            return fits(map_name)
        except Exception:
            pass
    return map_name in _attr(agent, "good_maps", [])


def _effective_util(agent) -> set:
    """Agent utility, padded with role defaults so thin data can't zero out."""
    role = _attr(agent, "role", "")
    return set(_attr(agent, "utility", [])) | ROLE_DEFAULT_UTIL.get(role, set())


def _effective_tags(agent) -> set:
    role = _attr(agent, "role", "")
    return set(_attr(agent, "synergy_tags", [])) | ROLE_DEFAULT_TAGS.get(role, set())


def score_comp(agents: List, map_name: str, rules: Dict) -> Tuple[int, Dict]:
    """
    Score a team composition. Returns (total_score, breakdown).
    Clamped to [0, 100]. `rules` is accepted for compatibility but V3
    uses its own balanced defaults.
    """
    breakdown: Dict[str, int] = {}
    total = 0

    roles = [_attr(a, "role", "") for a in agents]
    duelist_count = roles.count("Duelist")

    tag_set, util_set = set(), set()
    for a in agents:
        tag_set |= _effective_tags(a)
        util_set |= _effective_util(a)

    has_smokes = any(_attr(a, "role", "") == "Controller"
                     and (_effective_util(a) & VISION_BLOCK) for a in agents)
    has_recon = bool(util_set & RECON_UTIL)
    has_flash = bool(util_set & FLASH_UTIL)
    has_post_plant = bool(util_set & POST_PLANT_UTIL)
    has_entry = "entry" in tag_set
    has_anchor = bool(tag_set & ANCHOR_TAGS)
    has_flank = bool(tag_set & FLANK_TAGS)
    has_zone = bool(tag_set & ZONE_TAGS) or bool(util_set & {"wall", "walls", "barrier"})

    # ── 1. Role Balance (30) ─────────────────────────────────────────────────
    role_score = 0
    if "Controller" in roles: role_score += 10
    if "Initiator" in roles:  role_score += 8
    if "Sentinel" in roles:   role_score += 7
    if 1 <= duelist_count <= 2: role_score += 5
    elif duelist_count == 0:    role_score += 2
    breakdown["Role Balance"] = min(role_score, 30)
    total += breakdown["Role Balance"]

    # ── 2. Map Fit (20) — good_maps OR proven meta tier ─────────────────────
    map_score = 0
    for a in agents:
        if _fits_map(a, map_name):
            map_score += 4
        elif _META_AVAILABLE and is_meta_loaded():
            if get_agent_tier(_attr(a, "name", ""), map_name) in ("S", "A"):
                map_score += 4
    breakdown["Map Fit"] = min(map_score, 20)
    total += breakdown["Map Fit"]

    # ── 3. Utility Coverage (20) ─────────────────────────────────────────────
    util_score = 0
    if has_smokes:     util_score += 7
    if has_recon:      util_score += 5
    if has_flash:      util_score += 4
    if has_post_plant: util_score += 4
    breakdown["Utility Coverage"] = min(util_score, 20)
    total += breakdown["Utility Coverage"]

    # ── 4. Synergy (15) — complementary combos ──────────────────────────────
    syn = 0
    if has_entry and has_flash:      syn += 4   # someone opens, someone enables
    if has_smokes and has_entry:     syn += 4   # executes are possible
    if has_recon and has_entry:      syn += 3   # info-led aggression
    if has_anchor and has_flank:     syn += 2   # full defensive structure
    if has_post_plant and has_zone:  syn += 2   # round-closing power
    breakdown["Synergy"] = min(syn, 15)
    total += breakdown["Synergy"]

    # ── 5. Meta Alignment (15) ───────────────────────────────────────────────
    meta_score = 0.0
    if _META_AVAILABLE and is_meta_loaded():
        for a in agents:
            tier = get_agent_tier(_attr(a, "name", ""), map_name)
            if tier == "S":   meta_score += 3.0
            elif tier == "A": meta_score += 2.0
            elif tier == "B": meta_score += 1.0
    else:
        meta_score = 7.5  # neutral half-credit when no meta data
    breakdown["Meta Alignment"] = min(round(meta_score), 15)
    total += breakdown["Meta Alignment"]

    # ── Penalties (soft, capped at -20) ──────────────────────────────────────
    pen = 0
    if "Controller" not in roles: pen -= 10
    if "Initiator" not in roles:  pen -= 6
    if "Sentinel" not in roles:   pen -= 6
    if duelist_count == 3:        pen -= 4
    elif duelist_count >= 4:      pen -= 8
    if not has_smokes:            pen -= 6
    if not has_recon:             pen -= 4
    if not has_flash:             pen -= 3
    if not has_entry:             pen -= 3
    pen = max(pen, -20)
    breakdown["Penalties"] = pen
    total += pen

    return max(0, min(100, total)), breakdown


def get_score_grade(score: int) -> Tuple[str, str]:
    if score >= 85:   return "S", "#00ff9f"
    elif score >= 70: return "A", "#7fff00"
    elif score >= 55: return "B", "#ffd700"
    elif score >= 40: return "C", "#ff8c00"
    else:             return "D", "#ff4444"


def get_score_label(score: int) -> str:
    if score >= 85:   return "Tournament Ready"
    elif score >= 70: return "Solid Comp"
    elif score >= 55: return "Playable"
    elif score >= 40: return "Needs Work"
    else:             return "Weak Comp"
