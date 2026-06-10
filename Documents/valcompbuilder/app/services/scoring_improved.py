"""
Improved Scoring System - More lenient, vstats.gg style
"""

def score_comp_improved(agents, map_name):
    """
    Score composition with improved, lenient algorithm
    Based on: role balance, meta viability, synergy, utility
    """
    if not agents or len(agents) < 5:
        return 0, "F"
    
    from app.services.meta_service import is_on_meta, get_agent_meta_tier
    
    breakdown = {}
    
    # 1. ROLE BALANCE (25 pts) - Lenient: just need 1 of each role
    role_count = {"Duelist": 0, "Controller": 0, "Initiator": 0, "Sentinel": 0}
    for agent in agents:
        role = agent.role
        if role in role_count:
            role_count[role] += 1
    
    roles_present = sum(1 for count in role_count.values() if count > 0)
    # Just need different roles, more is better but not required
    role_score = roles_present * 5  # 0-20 pts
    breakdown["Role Balance"] = min(role_score, 25)
    
    # 2. MAP FIT (25 pts) - Lenient: reward any meta agent, heavy on win rate
    from app.services.meta_service import get_agent_meta_tier, get_agent_meta_pick_rate, get_agent_meta_win_rate
    
    map_fit_score = 0
    for agent in agents:
        tier = get_agent_meta_tier(agent.name, map_name)
        pick_rate = get_agent_meta_pick_rate(agent.name, map_name)
        win_rate = get_agent_meta_win_rate(agent.name, map_name)
        
        # Reward agents with good win rates (50%+) heavily
        if win_rate >= 50:
            map_fit_score += 4
        # Reward meta agents (in VCT data)
        elif tier:
            map_fit_score += 2
        # Don't punish off-meta, just less reward
        else:
            map_fit_score += 1
    
    breakdown["Map Fit"] = min(map_fit_score, 25)
    
    # 3. AGENT SYNERGY (20 pts) - Reward shared utility
    synergy_tags = {}
    for agent in agents:
        for tag in agent.synergy_tags:
            synergy_tags[tag] = synergy_tags.get(tag, 0) + 1
    
    synergy_score = sum(count for count in synergy_tags.values() if count > 1) * 2
    breakdown["Synergy"] = min(synergy_score, 20)
    
    # 4. UTILITY COVERAGE (15 pts) - Lenient: any utility is good
    utility_coverage = len(set(agent.utility_type for agent in agents if hasattr(agent, 'utility_type')))
    utility_score = utility_coverage * 3
    breakdown["Utility"] = min(utility_score, 15)
    
    # 5. ATTACK/DEFENSE (10 pts) - Don't emphasize too much
    attack_agents = sum(1 for a in agents if a.role == "Duelist")
    defense_agents = sum(1 for a in agents if a.role == "Sentinel")
    
    attack_defense_score = (attack_agents * 2) + (defense_agents * 1)
    breakdown["Attack/Defense"] = min(attack_defense_score, 10)
    
    # Calculate total (lenient: max ~100)
    total_score = sum(breakdown.values())
    
    # Grade: More lenient thresholds
    if total_score >= 90:
        grade = "S"  # Exceptional
    elif total_score >= 75:
        grade = "A"  # Very Good
    elif total_score >= 60:
        grade = "B"  # Good
    elif total_score >= 45:
        grade = "C"  # Decent
    elif total_score >= 30:
        grade = "D"  # Weak
    else:
        grade = "F"  # Poor
    
    return int(total_score), grade, breakdown

def get_score_label(total_score):
    """Get label for score"""
    if total_score >= 90:
        return "🏆 Pro Tier"
    elif total_score >= 75:
        return "⭐ Strong"
    elif total_score >= 60:
        return "✅ Solid"
    elif total_score >= 45:
        return "👍 Viable"
    elif total_score >= 30:
        return "⚠️ Weak"
    else:
        return "❌ Poor"

def get_score_color(grade):
    """Get color for grade badge"""
    colors = {
        "S": "#ffd700",  # Gold
        "A": "#00d9ff",  # Cyan
        "B": "#0ea5e9",  # Blue
        "C": "#f59e0b",  # Amber
        "D": "#ef4444",  # Red
        "F": "#7f1d1d",  # Dark Red
    }
    return colors.get(grade, "#64748b")
