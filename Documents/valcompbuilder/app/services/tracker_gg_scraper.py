"""
Tracker.gg Web Scraping Service
Fetches user's agent statistics per map
"""
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import streamlit as st

# Cache for API results (5 minute TTL)
CACHE_TTL = 300  # 5 minutes
cache_store = {}

def get_cached_data(key: str):
    """Get data from cache if not expired"""
    if key in cache_store:
        data, timestamp = cache_store[key]
        if (datetime.now() - timestamp).seconds < CACHE_TTL:
            return data
    return None

def set_cache(key: str, data):
    """Store data in cache"""
    cache_store[key] = (data, datetime.now())

def scrape_player_stats(riot_name: str, tagline: str) -> dict:
    """
    Scrape player's agent stats from tracker.gg
    
    Args:
        riot_name: Player name (e.g., "Player")
        tagline: Player tag (e.g., "NA1")
    
    Returns:
        dict with agent stats per map
    """
    
    # Check cache first
    cache_key = f"{riot_name}#{tagline}"
    cached = get_cached_data(cache_key)
    if cached:
        return {"status": "cached", "data": cached}
    
    try:
        # URL format for tracker.gg
        url = f"https://tracker.gg/valorant/profile/pc/{riot_name.lower()}-%23{tagline}/agents"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract agent data
        agents_data = parse_agent_stats_from_html(soup)
        
        if agents_data:
            # Cache the result
            set_cache(cache_key, agents_data)
            return {"status": "success", "data": agents_data}
        else:
            return {"status": "error", "message": "Could not parse agent data"}
            
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out. Try again later."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"status": "error", "message": "Player not found. Check name and tag."}
        else:
            return {"status": "error", "message": f"Error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Scraping failed: {str(e)}"}

def parse_agent_stats_from_html(soup) -> dict:
    """
    Parse agent statistics from tracker.gg HTML
    Extracts win rate, pick rate, KD per agent
    """
    agents_stats = {}
    
    try:
        # Find agent cards/rows (HTML structure varies, adjust selectors as needed)
        agent_rows = soup.find_all('div', class_=['agent-card', 'agent-row', 'tr'])
        
        for row in agent_rows:
            # Extract agent name
            agent_name = None
            name_elem = row.find(['h3', 'span', 'div'], class_=['agent-name'])
            if name_elem:
                agent_name = name_elem.text.strip()
            
            # Extract stats
            win_rate = None
            pick_rate = None
            kd_ratio = None
            
            # Find stat elements
            stat_elems = row.find_all(['td', 'div'], class_=['stat'])
            for elem in stat_elems:
                text = elem.text.strip()
                if '%' in text:
                    if 'win' in text.lower() or 'wr' in text.lower():
                        win_rate = float(text.replace('%', '').strip())
                    elif 'pick' in text.lower() or 'pr' in text.lower():
                        pick_rate = float(text.replace('%', '').strip())
                elif 'kd' in text.lower() or ':' in text:
                    try:
                        kd_ratio = float(text.split(':')[0] if ':' in text else text)
                    except:
                        pass
            
            # Store if we have agent name and at least one stat
            if agent_name and (win_rate is not None or pick_rate is not None):
                agents_stats[agent_name] = {
                    "agent": agent_name,
                    "win_rate": win_rate or 0,
                    "pick_rate": pick_rate or 0,
                    "kd_ratio": kd_ratio or 0
                }
        
        return agents_stats if agents_stats else None
        
    except Exception as e:
        st.error(f"Parse error: {e}")
        return None

def get_player_agents_used(riot_name: str, tagline: str) -> dict:
    """
    Get player's most used agents with stats
    
    Returns:
        {
            "Jett": {"pick_rate": 45.2, "win_rate": 52.1, "kd": 1.18},
            "Omen": {"pick_rate": 32.1, "win_rate": 49.5, "kd": 0.98},
            ...
        }
    """
    result = scrape_player_stats(riot_name, tagline)
    
    if result["status"] == "success":
        return result["data"]
    else:
        return {"error": result.get("message", "Unknown error")}

def compare_with_meta(agent_stats: dict, meta_data: dict) -> dict:
    """
    Compare player's agent stats with meta stats
    Returns color coding (green=ahead, yellow=equal, red=behind)
    """
    comparison = {}
    
    for agent, stats in agent_stats.items():
        if agent in meta_data:
            meta_wr = meta_data[agent].get("win_rate", 50)
            player_wr = stats.get("win_rate", 0)
            
            diff = player_wr - meta_wr
            
            if diff > 3:
                status = "🟢 Above Meta"
            elif diff > -3:
                status = "🟡 In Line"
            else:
                status = "🔴 Below Meta"
            
            comparison[agent] = {
                "status": status,
                "player_wr": player_wr,
                "meta_wr": meta_wr,
                "difference": diff
            }
    
    return comparison

def get_best_agents_for_player(agent_stats: dict) -> list:
    """
    Recommend best agents for player based on their stats
    Returns list of agents sorted by win rate
    """
    if not agent_stats or "error" in agent_stats:
        return []
    
    sorted_agents = sorted(
        agent_stats.items(),
        key=lambda x: x[1].get("win_rate", 0),
        reverse=True
    )
    
    return [
        {
            "agent": name,
            "win_rate": stats.get("win_rate"),
            "pick_rate": stats.get("pick_rate"),
            "kd": stats.get("kd_ratio")
        }
        for name, stats in sorted_agents[:5]  # Top 5
    ]

