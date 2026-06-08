"""
Recommender — suggests agents to complete or improve a team comp.
"""
from typing import List, Tuple, Dict
from app.models.agent import Agent


def recommend_agents(
    selected: List[Agent],
    all_agents: List[Agent],
    map_name: str,
    rules: Dict,
    max_suggestions: int = 3,
) -> List[Dict]:
    """
    Given a partial or complete comp, recommend agents that would improve it.
    Returns a list of dicts with {agent, reason, priority}.
    """
    if len(selected) >= 5:
        return _suggest_replacements(selected, all_agents, map_name)

    selected_names = {a.name for a in selected}
    available = [a for a in all_agents if a.name not in selected_names]
    slots_left = 5 - len(selected)

    roles = [a.role for a in selected]
    all_tags = []
    for a in selected:
        all_tags.extend(a.synergy_tags)
    all_util = []
    for a in selected:
        all_util.extend(a.utility)

    needed_roles = []
    if "Controller" not in roles:
        needed_roles.append("Controller")
    if "Initiator" not in roles:
        needed_roles.append("Initiator")
    if "Sentinel" not in roles:
        needed_roles.append("Sentinel")
    duelist_count = roles.count("Duelist")
    if duelist_count == 0:
        needed_roles.append("Duelist")

    suggestions = []
    seen_roles = set()

    # Priority 1: Fill missing critical roles
    for role in needed_roles:
        role_agents = [a for a in available if a.role == role]
        # Sort by map fit
        role_agents.sort(key=lambda a: (a.fits_map(map_name), a.name), reverse=True)
        if role_agents:
            agent = role_agents[0]
            reason = _build_reason(agent, map_name, selected, roles, all_util)
            suggestions.append({
                "agent": agent,
                "reason": reason,
                "priority": "high",
            })
            seen_roles.add(role)

    # Priority 2: Map-fit agents for remaining slots
    if len(suggestions) < slots_left:
        remaining = [a for a in available if a.name not in {s["agent"].name for s in suggestions}]
        map_fit = [a for a in remaining if a.fits_map(map_name)]
        map_fit.sort(key=lambda a: (len(a.synergy_tags), a.name), reverse=True)
        for agent in map_fit:
            if len(suggestions) >= slots_left:
                break
            if len(suggestions) >= max_suggestions:
                break
            reason = _build_reason(agent, map_name, selected, roles, all_util)
            suggestions.append({
                "agent": agent,
                "reason": reason,
                "priority": "medium",
            })

    return suggestions[:max_suggestions]


def _build_reason(agent: Agent, map_name: str, selected: List[Agent], roles: List[str], all_util: List[str]) -> str:
    """Construct a human-readable reason for recommending an agent."""
    reasons = []

    # Role gap
    if agent.role == "Controller" and "Controller" not in roles:
        reasons.append(f"your comp needs smokes")
    if agent.role == "Initiator" and "Initiator" not in roles:
        reasons.append(f"you have no opening utility")
    if agent.role == "Sentinel" and "Sentinel" not in roles:
        reasons.append(f"you need a site anchor")
    if agent.role == "Duelist" and "Duelist" not in roles:
        reasons.append(f"you have no entry fragger")

    # Map fit
    if agent.fits_map(map_name):
        reasons.append(f"they fit {map_name}")

    # Utility gap
    if "smokes" in agent.utility and "smokes" not in all_util:
        reasons.append(f"brings smokes your comp is missing")
    if any(t in agent.utility for t in ["flash", "paranoia"]) and "flash" not in all_util:
        reasons.append(f"adds flash utility")
    if any(t in agent.utility for t in ["recon-bolt", "drone", "haunt"]) and "recon" not in [u[:5] for u in all_util]:
        reasons.append(f"provides recon")

    if not reasons:
        reasons.append(f"adds {agent.role.lower()} presence to the team")

    return f"Pick {agent.name} because {' and '.join(reasons[:2])}."


def _suggest_replacements(selected: List[Agent], all_agents: List[Agent], map_name: str) -> List[Dict]:
    """Suggest improvements for a completed comp."""
    suggestions = []
    roles = [a.role for a in selected]
    all_util = []
    for a in selected:
        all_util.extend(a.utility)
    all_tags = []
    for a in selected:
        all_tags.extend(a.synergy_tags)

    duelist_count = roles.count("Duelist")

    # Find the weakest agent (one that doesn't fit the map and isn't covering gaps)
    for agent in selected:
        if not agent.fits_map(map_name):
            # Find a better option in the same role
            candidates = [
                a for a in all_agents
                if a.role == agent.role
                and a.name != agent.name
                and a.fits_map(map_name)
                and a.name not in [s.name for s in selected]
            ]
            if candidates:
                best = candidates[0]
                suggestions.append({
                    "agent": best,
                    "reason": f"Replace {agent.name} with {best.name} — {best.name} fits {map_name} better.",
                    "replaces": agent.name,
                    "priority": "medium",
                })
                if len(suggestions) >= 2:
                    break

    # Duelist overload
    if duelist_count >= 3:
        duelists = [a for a in selected if a.role == "Duelist"]
        target = duelists[-1]
        alternatives = [a for a in all_agents if a.role in ("Initiator", "Sentinel") and a.fits_map(map_name)]
        if alternatives:
            best_alt = alternatives[0]
            suggestions.append({
                "agent": best_alt,
                "reason": f"Replace {target.name} with {best_alt.name} — too many Duelists, need more utility.",
                "replaces": target.name,
                "priority": "high",
            })

    return suggestions[:3]
