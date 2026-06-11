"""Data loader service"""
import json
import os
from app.services.meta_service import is_on_meta, get_agent_meta_tier

class Agent:
    def __init__(self, name, role, icon="👤", synergy_tags=None, strengths=None, good_maps=None):
        self.name = name
        self.role = role
        self.icon = icon
        self.synergy_tags = synergy_tags or []
        self.strengths = strengths or []
        self.good_maps = good_maps or []
    
    def fits_map(self, map_name):
        """Check if agent is meta on map (VCT tier S or A)"""
        return is_on_meta(self.name, map_name)
    
    def get_map_tier(self, map_name):
        """Get VCT tier (S, A, B, C) for this agent on map"""
        return get_agent_meta_tier(self.name, map_name)

def load_agents():
    """Load agents with proper data"""
    agents = [
        # Duelists
        Agent("Jett", "Duelist", "⚔️", ["aggressive", "entry", "fast-push"], ["Mobility", "Entry fragging"], ["Haven", "Ascent", "Split"]),
        Agent("Reyna", "Duelist", "⚔️", ["aggressive", "self-sustain"], ["Self-heal", "Exit fragging"], ["Ascent", "Bind"]),
        Agent("Raze", "Duelist", "⚔️", ["aggressive", "site-clear"], ["Satchel plays", "Post-plant"], ["Split", "Breeze"]),
        Agent("Phoenix", "Duelist", "⚔️", ["aggressive", "entry"], ["Molly damage", "Healing"], ["Haven", "Pearl"]),
        Agent("Yoru", "Duelist", "⚔️", ["flanker", "entry"], ["Teleport", "Decoys"], ["Split", "Icebox"]),
        Agent("Neon", "Duelist", "⚔️", ["aggressive", "fast-push"], ["Speed boost", "Slide"], ["Breeze", "Pearl"]),
        Agent("Iso", "Duelist", "⚔️", ["aggressive"], ["1v1 potential"], ["Haven", "Lotus"]),
        Agent("Waylay", "Duelist", "⚔️", ["aggressive", "entry"], ["Entry utility"], ["Ascent", "Pearl"]),
        
        # Controllers
        Agent("Omen", "Controller", "💨", ["smokes", "defensive"], ["Smoke control", "Info"], ["Haven", "Ascent", "Split"]),
        Agent("Astra", "Controller", "💨", ["smokes", "recon"], ["Global utility", "Info"], ["Ascent", "Haven"]),
        Agent("Brimstone", "Controller", "💨", ["smokes", "plant-util"], ["Stim beacon", "Molly"], ["Split", "Icebox"]),
        Agent("Harbor", "Controller", "💨", ["defensive", "anchor"], ["Water walls", "Site control"], ["Bind", "Lotus"]),
        Agent("Viper", "Controller", "💨", ["smokes", "defensive"], ["Poison", "Wall"], ["Bind", "Icebox"]),
        
        # Initiators
        Agent("Sova", "Initiator", "🔍", ["information", "recon"], ["Drone info", "Drone executes"], ["Ascent", "Breeze"]),
        Agent("Breach", "Initiator", "🔍", ["aggressive", "entry"], ["Flashes", "Damage"], ["Haven", "Split"]),
        Agent("Skye", "Initiator", "🔍", ["information", "recon"], ["Bird info", "Healing"], ["Haven", "Ascent"]),
        Agent("Fade", "Initiator", "🔍", ["information", "recon"], ["Haunt info", "Damage"], ["Split", "Lotus"]),
        Agent("Gekko", "Initiator", "🔍", ["aggressive", "plant-util"], ["Mosh pit", "Plant drone"], ["Breeze", "Lotus"]),
        Agent("KAY/O", "Initiator", "🔍", ["aggressive", "entry"], ["Flash", "Suppression"], ["Ascent", "Split"]),
        Agent("Tejo", "Initiator", "🔍", ["aggressive", "entry"], ["Suppression", "Utility"], ["Ascent", "Fracture"]),
        
        # Sentinels
        Agent("Sage", "Sentinel", "🛡️", ["defensive", "anchor"], ["Healing", "Wall"], ["Haven", "Ascent"]),
        Agent("Killjoy", "Sentinel", "🛡️", ["defensive", "anchor"], ["Turret", "Alarm bot"], ["Ascent", "Icebox"]),
        Agent("Cypher", "Sentinel", "🛡️", ["defensive", "flank-control"], ["Cages", "Tripwire"], ["Split", "Icebox"]),
        Agent("Chamber", "Sentinel", "🛡️", ["anchor", "defensive"], ["OP wall", "Teleport"], ["Ascent", "Haven"]),
        Agent("Clove", "Controller", "🛡️", ["defensive", "anchor"], ["Healing", "Utility"], ["Pearl", "Split"]),
	Agent("Vyse", "Sentinel", "🛡️", ["defensive", "zone-control"], ["Arc rose", "Walls"], ["Ascent", "Pearl"]),
        Agent("Deadlock", "Sentinel", "🛡️", ["defensive", "anchor"], ["Locks", "Utility"], ["Ascent", "Icebox"]),
    ]
    return agents

def load_maps():
    """Load maps from data file or return defaults"""
    return [
        {"name": "Haven", "icon": "🏛️", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Ascent", "icon": "🏢", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Split", "icon": "🌉", "key_features": [], "preferred_roles": [], "attack_sided": True, "defense_sided": False},
        {"name": "Breeze", "icon": "🏖️", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Fracture", "icon": "⚡", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Icebox", "icon": "❄️", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Lotus", "icon": "🌸", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Pearl", "icon": "🐚", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": False},
        {"name": "Bind", "icon": "🔗", "key_features": [], "preferred_roles": [], "attack_sided": False, "defense_sided": True},
    ]

def load_rules():
    """Load validation rules"""
    return {}

def get_map_by_name(name):
    """Get map by name"""
    maps = load_maps()
    return next((m for m in maps if m["name"] == name), None)

def save_comp(comp_data):
    """Save a composition"""
    pass
