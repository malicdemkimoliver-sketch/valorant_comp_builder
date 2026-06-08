"""
Scoring engine — evaluates a team composition and returns a score from 0–100.

Scoring breakdown:
  Role Balance    (up to 25 pts): Controller, Initiator, Sentinel, Duelist count
  Map Fit         (up to 20 pts): How many agents are on their good_maps list
  Agent Synergy   (up to 20 pts): Shared synergy tags between agents
  Utility Coverage(up to 15 pts): Smokes, recon, flash, post-plant coverage
  Attack Strength (up to 10 pts): Entry, aggressive tags
  Defense Strength(up to 10 pts): Anchor, defensive, flank-control tags

Penalties are applied for missing critical roles/utility.
"""
from typing import List, Dict, Tuple
from app.models.agent import Agent
from app.models.comp import Comp


def score_comp(agents: List[Agent], map_name: str, rules: Dict) -> Tuple[int, Dict]:
    """
    Score a team composition.
    Returns (total_score, score_breakdown_dict).
    Score is clamped to [0, 100].
    """
    breakdown = {}
    total = 0

    # ── 1. Role Balance (max 25) ──────────────────────────────────────────────
    weights = rules["scoring_weights"]
    role_w = weights["role_balance"]["breakdown"]
    role_score = 0
    roles = [a.role for a in agents]

    if "Controller" in roles:
        role_score += role_w["has_controller"]
    if "Initiator" in roles:
        role_score += role_w["has_initiator"]
    if "Sentinel" in roles:
        role_score += role_w["has_sentinel"]

    duelist_count = roles.count("Duelist")
    if 1 <= duelist_count <= 2:
        role_score += role_w["duelist_count_optimal"]
    elif duelist_count == 0:
        role_score += 2  # minor reward for unusual but valid approach

    breakdown["Role Balance"] = min(role_score, weights["role_balance"]["weight"])
    total += breakdown["Role Balance"]

    # ── 2. Map Fit (max 20) ──────────────────────────────────────────────────
    map_w = weights["map_fit"]["breakdown"]
    map_score = sum(map_w["per_agent_on_good_map"] for a in agents if a.fits_map(map_name))
    breakdown["Map Fit"] = min(map_score, weights["map_fit"]["weight"])
    total += breakdown["Map Fit"]

    # ── 3. Agent Synergy (max 20) ────────────────────────────────────────────
    all_tags = []
    for a in agents:
        all_tags.extend(a.synergy_tags)
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    synergy_w = weights["synergy"]["breakdown"]
    # Tags that appear in 2+ agents count as synergy
    shared = sum(count - 1 for count in tag_counts.values() if count >= 2)
    synergy_score = min(shared * synergy_w["per_shared_tag"], weights["synergy"]["weight"])
    breakdown["Agent Synergy"] = synergy_score
    total += synergy_score

    # ── 4. Utility Coverage (max 15) ─────────────────────────────────────────
    util_w = weights["utility_coverage"]["breakdown"]
    all_util = []
    for a in agents:
        all_util.extend(a.utility)
    util_score = 0
    if "smokes" in all_util:
        util_score += util_w["has_smokes"]
    if any(t in all_util for t in ["recon-bolt", "drone", "haunt", "camera", "tripwire"]):
        util_score += util_w["has_recon"]
    if any(t in all_util for t in ["flash", "paranoia"]):
        util_score += util_w["has_flash"]
    if any(t in all_util for t in ["post-plant", "nanoswarm", "snake-bite", "shock-dart", "orbital"]):
        util_score += util_w["has_post_plant"]
    breakdown["Utility Coverage"] = min(util_score, weights["utility_coverage"]["weight"])
    total += breakdown["Utility Coverage"]

    # ── 5. Attack Strength (max 10) ──────────────────────────────────────────
    atk_w = weights["attack_strength"]["breakdown"]
    atk_score = 0
    all_synergy = []
    for a in agents:
        all_synergy.extend(a.synergy_tags)
    if "entry" in all_synergy:
        atk_score += atk_w["entry_tag"]
    if "aggressive" in all_synergy:
        atk_score += atk_w["aggressive_tag"]
    if "flash" in all_util:
        atk_score += atk_w["flash_for_entry"]
    breakdown["Attack Strength"] = min(atk_score, weights["attack_strength"]["weight"])
    total += breakdown["Attack_Strength"] if "Attack_Strength" in breakdown else breakdown["Attack Strength"]

    # ── 6. Defense Strength (max 10) ─────────────────────────────────────────
    def_w = weights["defense_strength"]["breakdown"]
    def_score = 0
    if "anchor" in all_synergy:
        def_score += def_w["anchor_tag"]
    if "defensive" in all_synergy:
        def_score += def_w["defensive_tag"]
    if "flank-control" in all_synergy:
        def_score += def_w["flank_control_tag"]
    breakdown["Defense Strength"] = min(def_score, weights["defense_strength"]["weight"])
    total += breakdown["Defense Strength"]

    # ── Penalties ─────────────────────────────────────────────────────────────
    penalties = rules["penalties"]
    if "Controller" not in roles:
        total += penalties["no_controller"]
    if "Initiator" not in roles:
        total += penalties["no_initiator"]
    if "Sentinel" not in roles:
        total += penalties["no_sentinel"]
    if duelist_count >= 3:
        total += penalties["too_many_duelists"]
    if "smokes" not in all_util:
        total += penalties["no_smokes"]
    if not any(t in all_util for t in ["recon-bolt", "drone", "haunt", "camera", "tripwire"]):
        total += penalties["no_recon"]
    if "flash" not in all_util and "paranoia" not in all_util:
        total += penalties["no_flash"]
    if "entry" not in all_synergy:
        total += penalties["no_entry"]
    # Low map fit penalty
    on_good_map = sum(1 for a in agents if a.fits_map(map_name))
    if on_good_map < 2:
        total += penalties["low_map_fit"]

    breakdown["Penalties"] = total - sum(v for k, v in breakdown.items() if k != "Penalties")

    return max(0, min(100, total)), breakdown


def get_score_grade(score: int) -> Tuple[str, str]:
    """Return a letter grade and color for a given score."""
    if score >= 85:
        return "S", "#00ff9f"
    elif score >= 70:
        return "A", "#7fff00"
    elif score >= 55:
        return "B", "#ffd700"
    elif score >= 40:
        return "C", "#ff8c00"
    else:
        return "D", "#ff4444"


def get_score_label(score: int) -> str:
    """Return a descriptive label for the score."""
    if score >= 85:
        return "Tournament Ready"
    elif score >= 70:
        return "Solid Comp"
    elif score >= 55:
        return "Playable"
    elif score >= 40:
        return "Needs Work"
    else:
        return "Weak Comp"
