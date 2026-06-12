"""Simple JSON-based database for saved comps and users"""
import json
import os
from datetime import datetime

# Deployment: set DB_PATH to a file on a persistent volume (e.g. /data/db.json)
# — the repo-relative default lives on an ephemeral filesystem on Railway.
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "db.json"),
)

def ensure_db():
    """Create database if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        init_db = {"users": {}, "comps": {}}
        with open(DB_PATH, 'w') as f:
            json.dump(init_db, f, indent=2)

def read_db():
    """Read database"""
    ensure_db()
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def write_db(data):
    """Write database"""
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def add_or_update_user(user_email, user_name=""):
    """Add or update user"""
    db = read_db()
    if user_email not in db["users"]:
        db["users"][user_email] = {"name": user_name, "created_at": datetime.now().isoformat(), "comps": []}
    write_db(db)

def save_comp(user_email, comp_data):
    """Save comp for user"""
    add_or_update_user(user_email)
    db = read_db()
    comp_id = f"{comp_data['map']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    comp_data['id'] = comp_id
    comp_data['saved_at'] = datetime.now().isoformat()
    
    if user_email not in db["comps"]:
        db["comps"][user_email] = []
    db["comps"][user_email].append(comp_data)
    write_db(db)
    return comp_id

def get_user_comps(user_email):
    """Get all comps for user"""
    db = read_db()
    return db["comps"].get(user_email, [])

def delete_comp(user_email, comp_id):
    """Delete comp"""
    db = read_db()
    if user_email in db["comps"]:
        db["comps"][user_email] = [c for c in db["comps"][user_email] if c.get("id") != comp_id]
    write_db(db)

ensure_db()
