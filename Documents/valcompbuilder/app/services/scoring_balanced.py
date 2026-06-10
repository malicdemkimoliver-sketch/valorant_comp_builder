"""
Balanced Scoring System - Fair, not too strict
Focuses on role diversity, synergy, and viability
"""

def score_comp_balanced(agents, map_name):
    """
    Score composition with balanced algorithm
    More forgiving, rewards good practices without harsh penalties
    """
    if not agents or len(agents) < 5:
        return 0, "F", {}
    
    from app.services.meta_service import is_on_meta, get_agent_meta_tier
    
    breakdown = {}
    
    # 1. ROLE DIVERSITY (20 pts) - Essential for good comps
    role_count = {"Duelist": 0, "Controller": 0, "Initiator": 0, "Sentinel": 0}
    for agent in agents:
        role = agent.role
        if role in role_count:
            role_count[role] += 1
    
    roles_present = sum(1 for count in role_count.values() if count > 0)
    
    # Scoring: Need at least 3 different roles for good comp
    if roles_present >= 4:
        role_score = 20  # Perfect: all 4 roles
    elif roles_present == 3:
        role_score = 18  # Excellent: 3 roles (most comps)
    elif roles_present == 2:
        role_score = 12  # Okay: 2 roles (uncommon)
    else:
        role_score = 5   # Bad: 1 role only
    
    breakdown["Role Diversity"] = role_score
    
    # 2. AGENT SYNERGY (25 pts) - Rewards agents that work together
    synergy_tags = {}
    for agent in agents:
        for tag in agent.synergy_tags:
            synergy_tags[tag] = synergy_tags.get(tag, 0) + 1
    
    # Count overlapping synergies (agents with same tags work well together)
    synergy_score = 0
    for tag, count in synergy_tags.items():
        if count >= 2:  # At least 2 agents share this tag
            synergy_score += (count - 1) * 3  # Reward for each pair sharing tag
    
    # Bonus for high synergy comps
    if synergy_score >= 12:
        synergy_score = min(synergy_score + 3, 25)
    
    breakdown["Agent Synergy"] = min(synergy_score, 25)
    
    # 3. MAP VIABILITY (25 pts) - Agents should work on selected map
    from app.services.meta_service import get_agent_meta_pick_rate, get_agent_meta_win_rate
    
    map_viability_score = 0
    for agent in agents:
        tier = get_agent_meta_tier(agent.name, map_name)
        pick_rate = get_agent_meta_pick_rate(agent.name, map_name)
        win_rate = get_agent_meta_win_rate(agent.name, map_name)
        
        # Scoring based on actual viability
        if tier == "S":
            map_viability_score += 5  # S-tier (essential)
        elif tier == "A":
            map_viability_score += 4  # A-tier (strong)
        elif tier == "B":
            map_viability_score += 3  # B-tier (viable)
        elif tier == "C":
            map_viability_score += 1  # C-tier (niche, but valid)
        elif pick_rate > 0 or win_rate >= 48:
            map_viability_score += 2  # Some viability even without tier
        else:
            map_viability_score += 0  # No data or too weak
    
    breakdown["Map Viability"] = min(map_viability_score, 25)
    
    # 4. UTILITY COVERAGE (15 pts) - Diverse utility types
    utility_types = set()
    for agent in agents:
        if hasattr(agent, 'utility_type') and agent.utility_type:
            utility_types.add(agent.utility_type)
    
    utility_score = len(utility_types) * 3
    breakdown["Utility Coverage"] = min(utility_score, 15)
    
    # 5. ATTACK/DEFENSE BALANCE (15 pts) - Good offensive/defensive mix
    attack_agents = sum(1 for a in agents if a.role == "Duelist")
    defense_agents = sum(1 for a in agents if a.role == "Sentinel")
    
    # Ideal: 1-2 duelists, 2-3 sentinels, 1-2 controllers, 1-2 initiators
    attack_defense_score = 0
    
    if 1 <= attack_agents <= 2:
        attack_defense_score += 5
    elif attack_agents == 0:
        attack_defense_score += 2  # Too passive
    elif attack_agents >= 3:
        attack_defense_score += 3  # Too aggressive
    
    if 2 <= defense_agents <= 3:
        attack_defense_score += 5
    elif defense_agents <= 1:
        attack_defense_score += 2  # Not enough defense
    elif defense_agents >= 4:
        attack_defense_score += 3  # Too defensive
    
    if 1 <= sum(1 for a in agents if a.role == "Controller") <= 2:
        attack_defense_score += 3
    
    if 1 <= sum(1 for a in agents if a.role == "Initiator") <= 2:
        attack_defense_score += 2
    
    breakdown["Attack/Defense Balance"] = min(attack_defense_score, 15)
    
    # TOTAL SCORE
    total_score = sum(breakdown.values())
    
    # GRADES - More forgiving
    if total_score >= 85:
        grade = "S"  # Exceptional comp
    elif total_score >= 75:
        grade = "A"  # Strong comp
    elif total_score >= 60:
        grade = "B"  # Good comp
    elif total_score >= 45:
        grade = "C"  # Decent comp
    elif total_score >= 30:
        grade = "D"  # Weak comp
    else:
        grade = "F"  # Poor comp
    
    return int(total_score), grade, breakdown

def get_grade_color(grade):
    """Get color for grade badge"""
    colors = {
        "S": "#ffd700",  # Gold
        "A": "#00d9ff",  # Cyan
        "B": "#0ea5e9",  # Blue
        "C": "#f59e0b",  # Amber
        "D": "#ef4444",  # Red
        "F": "#7f1d1d",  # Dark red
    }
    return colors.get(grade, "#64748b")

def get_score_label(score):
    """Get descriptive label for score"""
    if score >= 85:
        return "🏆 Pro Tier"
    elif score >= 75:
        return "⭐ Competitive"
    elif score >= 60:
        return "✅ Solid Pick"
    elif score >= 45:
        return "👍 Playable"
    elif score >= 30:
        return "⚠️ Weak"
    else:
        return "❌ Poor"

