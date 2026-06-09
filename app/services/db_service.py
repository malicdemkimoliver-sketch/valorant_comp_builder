"""
Database service — SQLite for local/cloud persistence.
Stores users (Google auth) and their saved comps.
On Streamlit Cloud the DB file lives in /tmp (ephemeral per session),
so we also support Supabase via st.secrets for true persistence.
"""
import sqlite3, json, os, hashlib, tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

# On Streamlit Cloud the app dir is read-only — use a writable location.
_LOCAL_DB = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db', 'gyds.db')
_TMP_DB   = os.path.join(tempfile.gettempdir(), 'gyds_comp_helper.db')

def _resolve_db_path():
    try:
        os.makedirs(os.path.dirname(_LOCAL_DB), exist_ok=True)
        testfile = os.path.join(os.path.dirname(_LOCAL_DB), '.write_test')
        with open(testfile, 'w') as f:
            f.write('ok')
        os.remove(testfile)
        return _LOCAL_DB
    except Exception:
        return _TMP_DB

DB_PATH = _resolve_db_path()

# ── Schema ────────────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,
    email       TEXT UNIQUE NOT NULL,
    name        TEXT,
    picture     TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS saved_comps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    name        TEXT NOT NULL,
    map_name    TEXT,
    agents      TEXT,   -- JSON array
    score       INTEGER,
    grade       TEXT,
    strengths   TEXT,   -- JSON array
    weaknesses  TEXT,   -- JSON array
    warnings    TEXT,   -- JSON array
    notes       TEXT,
    is_public   INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_comps_user ON saved_comps(user_id);
"""

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.executescript(_SCHEMA)

# ── Users ─────────────────────────────────────────────────────────────────────
def upsert_user(google_id: str, email: str, name: str, picture: str) -> Dict:
    uid = hashlib.sha256(google_id.encode()).hexdigest()[:24]
    with _conn() as c:
        c.execute("""
            INSERT INTO users (id, email, name, picture)
            VALUES (?,?,?,?)
            ON CONFLICT(email) DO UPDATE SET name=excluded.name, picture=excluded.picture
        """, (uid, email, name, picture))
    return get_user_by_email(email)

def get_user_by_email(email: str) -> Optional[Dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None

# ── Comps ─────────────────────────────────────────────────────────────────────
def save_comp_db(user_id: str, name: str, map_name: str, agents: List[Dict],
                 score: int, grade: str, strengths: List, weaknesses: List,
                 warnings: List, notes: str = "", is_public: bool = False) -> int:
    with _conn() as c:
        cur = c.execute("""
            INSERT INTO saved_comps
              (user_id,name,map_name,agents,score,grade,strengths,weaknesses,warnings,notes,is_public)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (user_id, name, map_name,
              json.dumps(agents), score, grade,
              json.dumps(strengths), json.dumps(weaknesses),
              json.dumps(warnings), notes, int(is_public)))
        return cur.lastrowid

def get_user_comps(user_id: str) -> List[Dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM saved_comps WHERE user_id=? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            for key in ('agents','strengths','weaknesses','warnings'):
                d[key] = json.loads(d[key] or '[]')
            result.append(d)
        return result

def delete_comp_db(comp_id: int, user_id: str):
    with _conn() as c:
        c.execute("DELETE FROM saved_comps WHERE id=? AND user_id=?", (comp_id, user_id))

def get_public_comps(limit: int = 20) -> List[Dict]:
    with _conn() as c:
        rows = c.execute("""
            SELECT sc.*, u.name as author_name, u.picture as author_pic
            FROM saved_comps sc JOIN users u ON sc.user_id=u.id
            WHERE sc.is_public=1 ORDER BY sc.score DESC, sc.created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            for key in ('agents','strengths','weaknesses','warnings'):
                d[key] = json.loads(d[key] or '[]')
            result.append(d)
        return result

# Initialise on import — never let a DB error crash the whole app
try:
    init_db()
except Exception as _e:
    import sys
    print(f"[db_service] init warning: {_e}", file=sys.stderr)
