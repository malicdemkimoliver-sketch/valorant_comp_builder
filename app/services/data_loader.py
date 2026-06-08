"""
Data loader service — loads and saves all JSON data files.
"""
import json
import os
from typing import List, Dict, Any
from app.models.agent import Agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_json(filename: str) -> Any:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filename: str, data: Any) -> None:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_agents() -> List[Agent]:
    """Load all agents from agents.json."""
    raw = _load_json("agents.json")
    return [Agent.from_dict(a) for a in raw]


def load_maps() -> List[Dict]:
    """Load all map data from maps.json."""
    return _load_json("maps.json")


def load_rules() -> Dict:
    """Load scoring rules from rules.json."""
    return _load_json("rules.json")


def save_rules(rules: Dict) -> None:
    """Save updated scoring rules."""
    _save_json("rules.json", rules)


def load_saved_comps() -> List[Dict]:
    """Load all saved comps from saved_comps.json."""
    try:
        return _load_json("saved_comps.json")
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_comp(comp_data: Dict) -> None:
    """Append a new comp to saved_comps.json."""
    comps = load_saved_comps()
    comps.append(comp_data)
    _save_json("saved_comps.json", comps)


def delete_comp(index: int) -> None:
    """Delete a saved comp by index."""
    comps = load_saved_comps()
    if 0 <= index < len(comps):
        comps.pop(index)
        _save_json("saved_comps.json", comps)


def get_agent_by_name(name: str) -> Agent | None:
    """Find an agent by name."""
    agents = load_agents()
    for agent in agents:
        if agent.name == name:
            return agent
    return None


def get_map_by_name(name: str) -> Dict | None:
    """Find a map by name."""
    maps = load_maps()
    for m in maps:
        if m["name"] == name:
            return m
    return None
