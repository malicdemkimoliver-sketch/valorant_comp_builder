"""
Validator — checks a comp for warnings and issues.
"""
from typing import List, Tuple, Dict
from app.models.agent import Agent
from app.models.comp import Comp


def validate_comp(agents: List[Agent], map_name: str, rules: Dict) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate a team comp.
    Returns:
      - warnings: list of warning strings
      - strengths: list of strength strings
      - weaknesses: list of weakness strings
    """
    warnings = []
    strengths = []
    weaknesses = []

    warning_msgs = rules.get("warnings", {})
    roles = [a.role for a in agents]
    duelist_count = roles.count("Duelist")

    all_tags = []
    for a in agents:
        all_tags.extend(a.synergy_tags)

    all_util = []
    for a in agents:
        all_util.extend(a.utility)

    # ── Role warnings ─────────────────────────────────────────────────────────
    if "Controller" not in roles:
        warnings.append(warning_msgs.get("no_controller", "No Controller in comp."))
        weaknesses.append("No smokes / site control")

    if "Initiator" not in roles:
        warnings.append(warning_msgs.get("no_initiator", "No Initiator in comp."))
        weaknesses.append("No opening utility or information")

    if "Sentinel" not in roles:
        warnings.append(warning_msgs.get("no_sentinel", "No Sentinel in comp."))
        weaknesses.append("No site anchor or flank coverage")

    if duelist_count >= 3:
        warnings.append(warning_msgs.get("too_many_duelists", "Too many Duelists."))
        weaknesses.append("Lacking utility for structured plays")

    # ── Entry warning ─────────────────────────────────────────────────────────
    if "entry" not in all_tags:
        warnings.append(warning_msgs.get("no_entry_duelist", "No entry-focused agent."))
        weaknesses.append("Weak site entry")

    # ── Utility warnings ──────────────────────────────────────────────────────
    if "smokes" not in all_util:
        warnings.append(warning_msgs.get("no_smokes", "No smokes."))
        weaknesses.append("Cannot safely execute onto sites")

    has_recon = any(t in all_util for t in ["recon-bolt", "drone", "haunt", "camera", "tripwire"])
    if not has_recon:
        warnings.append(warning_msgs.get("no_recon", "No recon utility."))
        weaknesses.append("Playing blind without intel")

    has_post_plant = any(t in all_util for t in ["post-plant", "nanoswarm", "snake-bite", "shock-dart", "orbital"])
    if not has_post_plant:
        warnings.append(warning_msgs.get("no_post_plant", "No post-plant utility."))
        weaknesses.append("Weak post-plant presence")

    has_flank = "flank-control" in all_tags or "anchor" in all_tags
    if not has_flank:
        warnings.append(warning_msgs.get("no_flank_control", "No flank control."))
        weaknesses.append("Vulnerable to flanks and rotations")

    # ── Map fit ───────────────────────────────────────────────────────────────
    agents_on_map = [a for a in agents if a.fits_map(map_name)]
    if len(agents_on_map) < 2:
        warnings.append(warning_msgs.get("low_map_fit", "Low map fit for selected agents."))
        weaknesses.append(f"Poor agent-to-map synergy on {map_name}")

    # ── Strengths ─────────────────────────────────────────────────────────────
    if "Controller" in roles and "smokes" in all_util:
        strengths.append("Strong smoke coverage for site executes")
    if "Initiator" in roles and has_recon:
        strengths.append("Good information gathering and intel")
    if "Sentinel" in roles and has_flank:
        strengths.append("Solid site anchor and flank denial")
    if duelist_count <= 2 and "entry" in all_tags:
        strengths.append("Structured entry with proper support")
    if has_post_plant:
        strengths.append("Post-plant utility secures won rounds")
    if len(agents_on_map) >= 4:
        strengths.append(f"Excellent map fit for {map_name}")
    elif len(agents_on_map) >= 3:
        strengths.append(f"Good map fit for {map_name}")
    if "aggressive" in all_tags and "smokes" in all_util:
        strengths.append("Aggression supported by utility")
    if "information" in all_tags or has_recon:
        strengths.append("Information advantage over opponents")

    return warnings, strengths, weaknesses
