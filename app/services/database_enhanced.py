"""
Enhanced Database Service with proper schema and persistence
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/db.json')

def init_database():
    """Initialize database with proper schema"""
    schema = {
        "version": 2,
        "users": {},
        "compositions": {},
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_comps": 0,
            "total_users": 0
        }
    }
    
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        save_database(schema)
    return load_database()

def load_database() -> Dict:
    """Load database from JSON"""
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return init_database()

def save_database(db: Dict):
    """Save database to JSON"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def create_user(email: str, name: str) -> Dict:
    """Create new user"""
    db = load_database()
    
    if email in db["users"]:
        return {"error": "User exists", "user": db["users"][email]}
    
    user = {
        "email": email,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "comps": [],
        "settings": {
            "theme": "dark",
            "notifications": True,
            "mobile_mode": False
        },
        "stats": {
            "total_comps": 0,
            "favorite_agents": [],
            "favorite_maps": []
        }
    }
    
    db["users"][email] = user
    db["metadata"]["total_users"] = len(db["users"])
    save_database(db)
    
    return {"success": True, "user": user}

def get_user(email: str) -> Optional[Dict]:
    """Get user by email"""
    db = load_database()
    user = db["users"].get(email)
    if user:
        user["last_login"] = datetime.now().isoformat()
        db["users"][email] = user
        save_database(db)
    return user

def save_composition(email: str, comp_data: Dict) -> Dict:
    """Save composition for user"""
    db = load_database()
    
    if email not in db["users"]:
        return {"error": "User not found"}
    
    comp_id = f"comp_{datetime.now().timestamp()}"
    
    composition = {
        "id": comp_id,
        "user_email": email,
        "map": comp_data.get("map"),
        "agents": comp_data.get("agents", []),
        "score": comp_data.get("score"),
        "grade": comp_data.get("grade"),
        "created_at": datetime.now().isoformat(),
        "notes": comp_data.get("notes", ""),
        "is_favorite": False
    }
    
    db["compositions"][comp_id] = composition
    db["users"][email]["comps"].append(comp_id)
    db["users"][email]["stats"]["total_comps"] = len(db["users"][email]["comps"])
    db["metadata"]["total_comps"] = len(db["compositions"])
    
    save_database(db)
    
    return {"success": True, "composition": composition}

def get_user_compositions(email: str) -> List[Dict]:
    """Get all compositions for user"""
    db = load_database()
    user = db["users"].get(email)
    
    if not user:
        return []
    
    comps = []
    for comp_id in user["comps"]:
        if comp_id in db["compositions"]:
            comps.append(db["compositions"][comp_id])
    
    return comps

def delete_composition(comp_id: str, email: str) -> Dict:
    """Delete composition"""
    db = load_database()
    
    comp = db["compositions"].get(comp_id)
    if not comp or comp.get("user_email") != email:
        return {"error": "Unauthorized"}
    
    db["compositions"].pop(comp_id, None)
    if email in db["users"]:
        db["users"][email]["comps"] = [c for c in db["users"][email]["comps"] if c != comp_id]
        db["users"][email]["stats"]["total_comps"] = len(db["users"][email]["comps"])
    
    db["metadata"]["total_comps"] = len(db["compositions"])
    save_database(db)
    
    return {"success": True}

def update_user_settings(email: str, settings: Dict) -> Dict:
    """Update user settings"""
    db = load_database()
    
    if email not in db["users"]:
        return {"error": "User not found"}
    
    db["users"][email]["settings"].update(settings)
    save_database(db)
    
    return {"success": True, "user": db["users"][email]}

# Initialize on import
init_database()
