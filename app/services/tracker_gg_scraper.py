"""
Tracker.gg Web Scraper using Selenium
Renders JavaScript and extracts agent statistics
"""
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime
from typing import Optional, Dict
import re

# Cache for results
CACHE_TTL = 600  # 10 minutes
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

def get_player_agents_used(riot_name: str, tagline: str) -> dict:
    """
    Fetch player agent statistics by scraping tracker.gg
    
    Args:
        riot_name: Player name (e.g., "gydrenzin")
        tagline: Player tag (e.g., "1337")
    
    Returns:
        dict with agent stats
    """
    
    # Clean inputs
    tagline_clean = tagline.lstrip('#')
    riot_name_clean = riot_name.lower()
    
    player_identifier = f"{riot_name_clean}/{tagline_clean}"
    cache_key = f"tracker_gg:{player_identifier}"
    
    # Check cache first
    cached = get_cached_data(cache_key)
    if cached:
        return {"status": "cached", "data": cached, "from_cache": True}
    
    try:
        # Build tracker.gg URL
        url = f"https://tracker.gg/valorant/profile/pc/{riot_name_clean}-{tagline_clean}/agents"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Fetch page
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 404:
            return {
                "status": "error",
                "message": f"Player '{riot_name}#{tagline_clean}' not found on tracker.gg.",
                "data": None
            }
        elif response.status_code != 200:
            return {
                "status": "error",
                "message": f"HTTP Error {response.status_code}",
                "data": None
            }
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract agent data from page
        agents_stats = parse_tracker_gg_page(soup)
        
        if not agents_stats:
            return {
                "status": "error",
                "message": "Could not find agent data. Player may have no ranked matches.",
                "data": None
            }
        
        # Cache result
        set_cache(cache_key, agents_stats)
        
        return {
            "status": "success",
            "data": agents_stats,
            "from_cache": False
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timed out. Try again later.",
            "data": None
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Connection error. Check your internet.",
            "data": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "data": None
        }

def parse_tracker_gg_page(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Parse tracker.gg page HTML and extract agent statistics
    Looks for agent rows in the stats table
    """
    try:
        agents_stats = {}
        
        # Look for agent stat rows - adjust selectors based on page structure
        # Try multiple selector strategies
        
        # Strategy 1: Look for rows with agent images and stats
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                # Look for cells containing agent data
                cells = row.find_all('td')
                
                if len(cells) < 4:
                    continue
                
                # First cell usually contains agent name/image
                agent_cell = cells[0]
                agent_name_elem = agent_cell.find(['img', 'span', 'a'])
                
                if not agent_name_elem:
                    continue
                
                # Try to extract agent name
                agent_name = None
                
                # From image alt text
                if agent_name_elem.name == 'img':
                    agent_name = agent_name_elem.get('alt')
                
                # From text content
                if not agent_name:
                    agent_name = agent_cell.get_text(strip=True)
                
                if not agent_name or len(agent_name) < 2:
                    continue
                
                # Extract stats from other cells
                stats_text = [cell.get_text(strip=True) for cell in cells[1:]]
                
                # Try to find win rate, K/D, matches
                win_rate = extract_percentage(stats_text)
                kd_ratio = extract_ratio(stats_text)
                matches = extract_matches(stats_text)
                
                if win_rate is not None:
                    agents_stats[agent_name] = {
                        "agent": agent_name,
                        "win_rate": round(win_rate, 2),
                        "kd_ratio": round(kd_ratio, 2) if kd_ratio else 0,
                        "matches_played": matches if matches else 0,
                        "pick_rate": 0
                    }
            
            except Exception as e:
                continue
        
        # Calculate pick rates
        if agents_stats:
            total_matches = sum(a.get("matches_played", 0) for a in agents_stats.values())
            if total_matches > 0:
                for agent in agents_stats.values():
                    pick_rate = (agent.get("matches_played", 0) / total_matches) * 100
                    agent["pick_rate"] = round(pick_rate, 1)
        
        return agents_stats if agents_stats else None
        
    except Exception as e:
        return None

def extract_percentage(text_list: list) -> Optional[float]:
    """Extract percentage value from text list"""
    for text in text_list:
        match = re.search(r'(\d+\.?\d*)\s*%', text)
        if match:
            return float(match.group(1))
    return None

def extract_ratio(text_list: list) -> Optional[float]:
    """Extract K/D ratio"""
    for text in text_list:
        # Look for pattern like "1.23" or "1.5"
        match = re.search(r'(\d+\.\d{2})', text)
        if match:
            val = float(match.group(1))
            if 0 < val < 10:  # Reasonable K/D range
                return val
    return None

def extract_matches(text_list: list) -> Optional[int]:
    """Extract match count"""
    for text in text_list:
        # Look for numbers that could be match counts
        match = re.search(r'\b(\d{2,})\b', text)
        if match:
            val = int(match.group(1))
            if 5 < val < 1000:  # Reasonable match range
                return val
    return None

def get_best_agents_for_player(agent_stats: dict) -> list:
    """Get player's best agents sorted by win rate"""
    if not agent_stats:
        return []
    
    qualified_agents = {
        name: stats 
        for name, stats in agent_stats.items() 
        if stats.get("matches_played", 0) >= 5
    }
    
    sorted_agents = sorted(
        qualified_agents.items(),
        key=lambda x: x[1].get("win_rate", 0),
        reverse=True
    )
    
    return [
        {
            "agent": name,
            "win_rate": stats.get("win_rate"),
            "kd": stats.get("kd_ratio"),
            "matches": stats.get("matches_played")
        }
        for name, stats in sorted_agents[:5]
    ]

def clear_cache(player_identifier: str = None):
    """Clear cache"""
    global cache_store
    if player_identifier:
        cache_key = f"tracker_gg:{player_identifier}"
        if cache_key in cache_store:
            del cache_store[cache_key]
    else:
        cache_store.clear()

