"""
Meta Tracker Service — VCT pick rates, win rates, and tier classification
"""
import json
import os

def load_meta_data():
    """Load VCT meta data from JSON file"""
    try:
        path = os.path.join(os.path.dirname(__file__), '../../data/vct_meta.json')
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {"meta_by_map": {}, "tier_definitions": {}}

def get_agent_meta_tier(agent_name, map_name):
    """
    Get the VCT tier for an agent on a specific map
    Returns: tier (S, A, B, C) or None if not in meta
    """
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    agent_meta = map_meta.get(agent_name, {})
    return agent_meta.get("tier")

def get_agent_meta_pick_rate(agent_name, map_name):
    """Get pick rate % for agent on map"""
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    agent_meta = map_meta.get(agent_name, {})
    return agent_meta.get("pick_rate", 0)

def get_agent_meta_win_rate(agent_name, map_name):
    """Get win rate % for agent on map"""
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    agent_meta = map_meta.get(agent_name, {})
    return agent_meta.get("win_rate", 0)

def is_on_meta(agent_name, map_name):
    """
    Check if agent is on-meta for this specific map.
    Simple & accurate: If it's in VCT data for this map, pros play it = it's meta.
    """
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    return agent_name in map_meta

def is_off_meta(agent_name, map_name):
    """Check if agent is off-meta (not in VCT data for this map)"""
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    return agent_name not in map_meta

def get_tier_color(tier):
    """Get color for tier badge"""
    colors = {
        "S": "#ffd700",  # Gold
        "A": "#10b981",  # Green
        "B": "#f59e0b",  # Amber
        "C": "#ff4d6d",  # Red
    }
    return colors.get(tier, "#64748b")

def get_tier_description(tier):
    """Get description for tier"""
    meta = load_meta_data()
    definitions = meta.get("tier_definitions", {})
    return definitions.get(tier, "Unknown tier")

def get_all_meta_agents_for_map(map_name):
    """Get all agents with their meta tiers for a map"""
    meta = load_meta_data()
    map_meta = meta.get("meta_by_map", {}).get(map_name, {})
    return map_meta

def get_best_agents_for_map(map_name, tier=None):
    """Get agents for a map, optionally filtered by tier"""
    map_meta = get_all_meta_agents_for_map(map_name)
    if not tier:
        return list(map_meta.keys())
    return [name for name, data in map_meta.items() if data.get("tier") == tier]

