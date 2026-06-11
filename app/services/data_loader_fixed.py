"""
Fixed Data Loader - Vyse moved to Sentinel (was wrongly listed as Controller)
"""
import json
import os

class Agent:
    def __init__(self, name, role, utility_type, synergy_tags, attack_potential, defense_potential):
        self.name = name
        self.role = role
        self.utility_type = utility_type
        self.synergy_tags = synergy_tags
        self.attack_potential = attack_potential
        self.defense_potential = defense_potential
    
    def fits_map(self, map_name):
        """Check if agent is meta on map"""
        from app.services.meta_service import is_on_meta
        return is_on_meta(self.name, map_name)
    
    def get_map_tier(self, map_name):
        """Get VCT tier for this map"""
        from app.services.meta_service import get_agent_meta_tier
        return get_agent_meta_tier(self.name, map_name)

def load_agents():
    """Load all agents with corrected roles"""
    return [
        # DUELISTS (8)
        Agent("Jett", "Duelist", "Mobility", ["duelist"], 90, 40),
        Agent("Reyna", "Duelist", "Self-Heal", ["duelist", "heal"], 95, 30),
        Agent("Raze", "Duelist", "Area Denial", ["duelist", "damage"], 90, 50),
        Agent("Phoenix", "Duelist", "Self-Heal", ["duelist", "heal", "fire"], 85, 35),
        Agent("Yoru", "Duelist", "Deception", ["duelist", "infiltration"], 85, 25),
        Agent("Neon", "Duelist", "Speed", ["duelist", "mobility"], 80, 30),
        Agent("Iso", "Duelist", "Isolation", ["duelist", "solo"], 85, 60),
        Agent("Waylay", "Duelist", "Traps", ["duelist", "area-denial"], 80, 50),
        
        # CONTROLLERS (5) - VYSE REMOVED FROM HERE
        Agent("Omen", "Controller", "Smoke", ["control", "info"], 60, 80),
        Agent("Astra", "Controller", "Smoke", ["control", "info"], 55, 85),
        Agent("Brimstone", "Controller", "Utility", ["control", "support"], 65, 75),
        Agent("Harbor", "Controller", "Walls", ["control", "sentinel-assist"], 60, 85),
        Agent("Viper", "Controller", "Toxin", ["control", "damage"], 70, 80),
        
        # INITIATORS (7)
        Agent("Sova", "Initiator", "Recon", ["info", "utility"], 70, 75),
        Agent("Breach", "Initiator", "Crowd Control", ["cc", "utility"], 85, 60),
        Agent("Skye", "Initiator", "Recon", ["info", "heal"], 75, 70),
        Agent("Fade", "Initiator", "Recon", ["info", "utility"], 70, 75),
        Agent("Gekko", "Initiator", "Utility", ["utility", "gadget"], 65, 70),
        Agent("KAY/O", "Initiator", "Support", ["support", "flash"], 80, 60),
        Agent("Tejo", "Initiator", "Area Denial", ["area-denial"], 75, 70),
        
        # SENTINELS (7) - VYSE ADDED HERE
        Agent("Sage", "Sentinel", "Heal", ["heal", "support"], 50, 95),
        Agent("Killjoy", "Sentinel", "Utility", ["utility", "gadget"], 65, 90),
        Agent("Cypher", "Sentinel", "Recon", ["info", "utility"], 60, 85),
        Agent("Chamber", "Sentinel", "Utility", ["utility", "weapon"], 70, 80),
        Agent("Clove", "Sentinel", "Support", ["support", "gadget"], 65, 80),
        Agent("Deadlock", "Sentinel", "Traps", ["traps", "area-denial"], 60, 90),
        Agent("Vyse", "Sentinel", "Utility", ["control", "gadget"], 60, 85),  # FIXED: Was Controller, now Sentinel
    ]

def load_maps():
    """Load all maps"""
    return [
        {"name": "Ascent", "icon": "🏛️"},
        {"name": "Haven", "icon": "🌿"},
        {"name": "Split", "icon": "⚙️"},
        {"name": "Breeze", "icon": "❄️"},
        {"name": "Fracture", "icon": "⚡"},
        {"name": "Icebox", "icon": "🧊"},
        {"name": "Lotus", "icon": "🌸"},
        {"name": "Pearl", "icon": "🔵"},
        {"name": "Bind", "icon": "🌈"},
    ]

