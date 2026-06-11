"""
Scoring engine V4 — the classic six-category breakdown, powered by V3 internals.

Categories (totals 100):
  Role Balance     (25): Controller 8, Initiator 6, Sentinel 6, 1-2 Duelists 5
  Map Fit          (20): 4/agent — good_maps match OR S/A meta tier on the map
  Agent Synergy    (20): complementary combos (entry+flash, smokes+entry,
                         recon+entry, anchor+flank, post-plant+zone)
  Utility Coverage (15): smokes 5, recon 4, flash 3, post-plant 3
  Attack Strength  (10): entry 5, aggressive 3, flash support 2
  Defense Strength (10): anchor 4, defensive/zone 3, flank control 3

Kept from V3 (the fixes that stopped good comps scoring <50):
  - Role fallbacks: thin agent data inherits sensible defaults from its role
  - Vision-block smokes: Viper/Harbor walls and orbs count as smokes
  - Meta-aware map fit: S/A tier on a map counts as fitting it
  - Soft penalties capped at -20
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
    """Real utility data; role defaults ONLY when the agent has none at all."""
    real = set(_attr(agent, "utility", []))
    if real:
        return real
    return ROLE_DEFAULT_UTIL.get(_attr(agent, "role", ""), set())


def _effective_tags(agent) -> set:
    """Real synergy tags; role defaults ONLY when the agent has none at all."""
    real = set(_attr(agent, "synergy_tags", []))
    if real:
        return real
    return ROLE_DEFAULT_TAGS.get(_attr(agent, "role", ""), set())


def score_comp(agents: List, map_name: str, rules: Dict) -> Tuple[int, Dict]:
    """Score a comp. Returns (total 0-100, breakdown with classic categories)."""
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
    has_aggressive = "aggressive" in tag_set
    has_anchor = bool(tag_set & ANCHOR_TAGS)
    has_flank = bool(tag_set & FLANK_TAGS)
    has_zone = bool(tag_set & ZONE_TAGS) or bool(util_set & {"wall", "walls", "barrier"})

    # ── 1. Role Balance (25) ─────────────────────────────────────────────────
    role_score = 0
    if "Controller" in roles: role_score += 8
    if "Initiator" in roles:  role_score += 6
    if "Sentinel" in roles:   role_score += 6
    if 1 <= duelist_count <= 2: role_score += 5
    elif duelist_count == 0:    role_score += 2
    breakdown["Role Balance"] = min(role_score, 25)
    total += breakdown["Role Balance"]

    # ── 2. Map Fit (20) ──────────────────────────────────────────────────────
    map_score = 0
    for a in agents:
        if _fits_map(a, map_name):
            map_score += 4
        elif _META_AVAILABLE and is_meta_loaded():
            if get_agent_tier(_attr(a, "name", ""), map_name) in ("S", "A"):
                map_score += 4
    breakdown["Map Fit"] = min(map_score, 20)
    total += breakdown["Map Fit"]

    # ── 3. Agent Synergy (20) — complementary combos ─────────────────────────
    syn = 0
    if has_entry and has_flash:      syn += 5   # someone opens, someone enables
    if has_smokes and has_entry:     syn += 5   # executes are possible
    if has_recon and has_entry:      syn += 4   # info-led aggression
    if has_anchor and has_flank:     syn += 3   # full defensive structure
    if has_post_plant and has_zone:  syn += 3   # round-closing power
    breakdown["Agent Synergy"] = min(syn, 20)
    total += breakdown["Agent Synergy"]

    # ── 4. Utility Coverage (15) ─────────────────────────────────────────────
    util_score = 0
    if has_smokes:     util_score += 5
    if has_recon:      util_score += 4
    if has_flash:      util_score += 3
    if has_post_plant: util_score += 3
    breakdown["Utility Coverage"] = min(util_score, 15)
    total += breakdown["Utility Coverage"]

    # ── 5. Attack Strength (10) ──────────────────────────────────────────────
    atk = 0
    if has_entry:      atk += 5
    if has_aggressive: atk += 3
    if has_flash:      atk += 2
    breakdown["Attack Strength"] = min(atk, 10)
    total += breakdown["Attack Strength"]

    # ── 6. Defense Strength (10) ─────────────────────────────────────────────
    dfn = 0
    if has_anchor: dfn += 4
    if has_zone:   dfn += 3
    if has_flank:  dfn += 3
    breakdown["Defense Strength"] = min(dfn, 10)
    total += breakdown["Defense Strength"]

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
    if score >= 85:   return "S", "#00ff9f"   # mint green
    elif score >= 70: return "A", "#ffd700"   # gold
    elif score >= 55: return "B", "#ff9f43"   # amber
    elif score >= 40: return "C", "#ff6348"   # coral
    else:             return "D", "#ff4444"   # red


def get_score_label(score: int) -> str:
    if score >= 85:   return "Tournament Ready"
    elif score >= 70: return "Solid Comp"
    elif score >= 55: return "Playable"
    elif score >= 40: return "Needs Work"
    else:             return "Weak Comp"
