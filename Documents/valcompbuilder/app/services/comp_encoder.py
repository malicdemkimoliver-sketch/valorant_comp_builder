"""
Comp Encoder/Decoder
Converts comp (map + 5 agents) to short alphanumeric codes
Example: VAL-ASCENT-JT-OM-KJ-SK-GK
"""
import base64
import json
from typing import Dict, Tuple, Optional

# Agent name to 2-letter code mapping
AGENT_CODES = {
    "Astra": "AT",
    "Breach": "BR",
    "Brimstone": "BM",
    "Chamber": "CH",
    "Cypher": "CY",
    "Fade": "FD",
    "Gekko": "GK",
    "Harbor": "HB",
    "Omen": "OM",
    "Phoenix": "PX",
    "Raze": "RZ",
    "Reyna": "RN",
    "Sage": "SG",
    "Skye": "SK",
    "Sova": "SV",
    "Viper": "VP",
    "Yoru": "YR",
    "KAY/O": "KO",
    "Killjoy": "KJ",
    "Jett": "JT",
    "Neon": "NE",
    "Rift": "RF",
    "Twitch": "TW",
    "Iso": "IS",
    "Clove": "CL",
    "Vyse": "VY",
}

# Reverse mapping
CODE_TO_AGENT = {v: k for k, v in AGENT_CODES.items()}

# Map codes
MAP_CODES = {
    "Ascent": "AC",
    "Bind": "BD",
    "Breeze": "BZ",
    "Fracture": "FR",
    "Haven": "HV",
    "Icebox": "IB",
    "Lotus": "LT",
    "Pearl": "PL",
    "Split": "SP",
}

MAP_TO_CODE = {v: k for k, v in MAP_CODES.items()}


class CompEncoder:
    """Encode and decode team compositions"""
    
    VERSION = "2"  # Version for future compatibility
    PREFIX = "VAL"  # Valorant
    
    @staticmethod
    def encode(map_name: str, agents: list) -> str:
        """
        Encode a composition into a short code
        
        Args:
            map_name: Map name (e.g., "Ascent")
            agents: List of 5 agent names
            
        Returns:
            Short code (e.g., "VAL-AC-JT-OM-KJ-SK-SG")
        """
        if len(agents) != 5:
            raise ValueError("Composition must have exactly 5 agents")
        
        # Get map code
        map_code = MAP_CODES.get(map_name)
        if not map_code:
            raise ValueError(f"Unknown map: {map_name}")
        
        # Get agent codes
        agent_codes = []
        for agent in agents:
            code = AGENT_CODES.get(agent)
            if not code:
                raise ValueError(f"Unknown agent: {agent}")
            agent_codes.append(code)
        
        # Build comp code: VAL-VERSION-MAP-AGENT1-AGENT2-AGENT3-AGENT4-AGENT5
        comp_code = f"{CompEncoder.PREFIX}-{CompEncoder.VERSION}-{map_code}-{'-'.join(agent_codes)}"
        return comp_code
    
    @staticmethod
    def decode(comp_code: str) -> Tuple[str, list]:
        """
        Decode a short code into map and agents
        
        Args:
            comp_code: Short code (e.g., "VAL-2-AC-JT-OM-KJ-SK-SG")
            
        Returns:
            Tuple of (map_name, [agent_names])
        """
        parts = comp_code.strip().upper().split("-")
        
        if len(parts) < 4:
            raise ValueError("Invalid comp code format")
        
        if parts[0] != CompEncoder.PREFIX:
            raise ValueError(f"Invalid prefix. Expected {CompEncoder.PREFIX}")
        
        # Version check (parts[1])
        version = parts[1]
        
        # Map code (parts[2])
        map_code = parts[2]
        map_name = MAP_TO_CODE.get(map_code)
        if not map_name:
            raise ValueError(f"Unknown map code: {map_code}")
        
        # Agent codes (parts[3:])
        agent_codes = parts[3:]
        if len(agent_codes) != 5:
            raise ValueError(f"Expected 5 agents, got {len(agent_codes)}")
        
        agents = []
        for code in agent_codes:
            agent = CODE_TO_AGENT.get(code)
            if not agent:
                raise ValueError(f"Unknown agent code: {code}")
            agents.append(agent)
        
        return map_name, agents
    
    @staticmethod
    def get_available_agents() -> list:
        """Get list of all available agents"""
        return sorted(AGENT_CODES.keys())
    
    @staticmethod
    def get_available_maps() -> list:
        """Get list of all available maps"""
        return sorted(MAP_CODES.keys())


# Example usage:
if __name__ == "__main__":
    # Example encode
    comp = CompEncoder.encode("Ascent", ["Jett", "Omen", "Killjoy", "Skye", "Sage"])
    print(f"Encoded: {comp}")
    
    # Example decode
    decoded_map, decoded_agents = CompEncoder.decode(comp)
    print(f"Decoded map: {decoded_map}")
    print(f"Decoded agents: {decoded_agents}")
