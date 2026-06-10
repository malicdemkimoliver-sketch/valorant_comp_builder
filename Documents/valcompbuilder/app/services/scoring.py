"""Lenient scoring service matching original builder with VCT meta tiers"""
from app.services.meta_service import get_agent_meta_tier

def score_comp(agents, map_name, rules):
    """
    Score a composition (lenient version with VCT meta bonuses)
    - Role Balance (25 points)
    - Map Fit (20 points) — rewards S/A tier agents
    - Agent Synergy (20 points)
    - Utility Coverage (15 points)
    - Attack Strength (10 points)
    - Defense Strength (10 points)
    Total: 100 points
    """
    
    breakdown = {
        "Role Balance": 0,
        "Map Fit": 0,
        "Agent Synergy": 0,
        "Utility Coverage": 0,
        "Attack Strength": 0,
        "Defense Strength": 0,
    }
    
    if not agents:
        return 0, breakdown
    
    # 1. ROLE BALANCE (25 points) - More lenient
    roles = [a.role for a in agents]
    role_count = {
        "Duelist": roles.count("Duelist"),
        "Controller": roles.count("Controller"),
        "Initiator": roles.count("Initiator"),
        "Sentinel": roles.count("Sentinel"),
    }
    
    # Award points for role variety (any non-zero role is good)
    roles_present = sum(1 for count in role_count.values() if count > 0)
    breakdown["Role Balance"] = min(roles_present * 5, 25)
    
    # 2. MAP FIT (20 points) — VCT tier-based scoring
    # S tier = 5 pts (essential meta)
    # A tier = 4 pts (strong meta)
    # B tier = 3 pts (viable meta)
    # C tier = 1 pt (niche pick)
    # Not in data = 0 pts (not viable)
    from app.services.meta_service import get_agent_meta_tier
    
    tier_scores = {"S": 5, "A": 4, "B": 3, "C": 1, None: 0}
    map_fit_score = sum(tier_scores.get(get_agent_meta_tier(agent.name, map_name), 0) for agent in agents)
    
    # Cap at 20 points
    breakdown["Map Fit"] = min(map_fit_score, 20)
    
    # 3. AGENT SYNERGY (20 points) - More generous
    all_tags = []
    for a in agents:
        all_tags.extend(a.synergy_tags)
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    synergy_score = sum(min(count - 1, 3) for count in tag_counts.values() if count > 1)
    breakdown["Agent Synergy"] = min(synergy_score * 3, 20)
    
    # 4. UTILITY COVERAGE (15 points) - More generous
    utility_tags = ["smokes", "information", "defensive", "plant-util", "aggressive"]
    coverage = len(set(tag for a in agents for tag in a.synergy_tags if tag in utility_tags))
    breakdown["Utility Coverage"] = min(coverage * 3 + 5, 15)
    
    # 5. ATTACK STRENGTH (10 points) - Easier to achieve
    attack_agents = sum(1 for a in agents if any(tag in a.synergy_tags for tag in ["aggressive", "entry", "fast-push"]))
    breakdown["Attack Strength"] = min(attack_agents * 2 + 2, 10)
    
    # 6. DEFENSE STRENGTH (10 points) - Easier to achieve
    defense_agents = sum(1 for a in agents if any(tag in a.synergy_tags for tag in ["defensive", "anchor", "flank-control"]))
    breakdown["Defense Strength"] = min(defense_agents * 2 + 2, 10)
    
    # Calculate total score
    total_score = sum(breakdown.values())
    return total_score, breakdown

def get_score_grade(score):
    """Get grade and color for score"""
    if score >= 85:
        return "S", "#ffd700"  # Gold
    elif score >= 75:
        return "A", "#00ff9f"  # Cyan
    elif score >= 65:
        return "B", "#0ea5e9"  # Blue
    elif score >= 55:
        return "C", "#f59e0b"  # Amber
    elif score >= 45:
        return "D", "#ff4d6d"  # Red
    else:
        return "F", "#ff0000"  # Dark Red

def get_score_label(score):
    """Get descriptive label for score"""
    if score >= 90:
        return "Elite Comp - Tournament Ready"
    elif score >= 80:
        return "Excellent Comp - Highly Recommended"
    elif score >= 70:
        return "Good Comp - Solid Strategy"
    elif score >= 60:
        return "Viable Comp - Needs Refinement"
    elif score >= 50:
        return "Playable - Many Issues"
    else:
        return "Poor Comp - Rework Needed"
