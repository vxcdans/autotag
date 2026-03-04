import sqlite3
import threading
import time
from typing import List, Optional, Tuple

DB_PATH = "tagall.db"
_db_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    # ========== EXISTING TABLES ==========
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tagall_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER UNIQUE,
        group_title TEXT,
        date_added TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tagall_sessions (
        group_id INTEGER PRIMARY KEY,
        started_at INTEGER,
        is_active INTEGER
    )
    """)

    # ========== NEW TABLE FOR LIVEGRAM ==========
    cur.execute("""
    CREATE TABLE IF NOT EXISTS livegram_map (
        admin_msg_id INTEGER PRIMARY KEY,
        user_id INTEGER
    )
    """)

    conn.commit()
    return conn

_db = init_db()

# =========================================================
# TAGALL GROUP HELPERS
# =========================================================
def add_group(group_id: int, title: Optional[str] = None):
    with _db_lock:
        cur = _db.cursor()
        cur.execute("INSERT OR IGNORE INTO tagall_groups (group_id, group_title, date_added) VALUES (?, ?, ?)",
                    (group_id, title or "", time.strftime('%Y-%m-%d %H:%M:%S')))
        _db.commit()

def remove_group(group_id: int):
    with _db_lock:
        cur = _db.cursor()
        cur.execute("DELETE FROM tagall_groups WHERE group_id = ?", (group_id,))
        _db.commit()

def list_groups() -> List[Tuple[int, str]]:
    with _db_lock:
        cur = _db.cursor()
        cur.execute("SELECT group_id, group_title FROM tagall_groups ORDER BY id")
        return cur.fetchall()

# =========================================================
# TAGALL SESSION HELPERS
# =========================================================
def start_session(group_id: int):
    with _db_lock:
        cur = _db.cursor()
        cur.execute("REPLACE INTO tagall_sessions (group_id, started_at, is_active) VALUES (?, ?, 1)",
                    (group_id, int(time.time())))
        _db.commit()

def stop_session(group_id: int):
    with _db_lock:
        cur = _db.cursor()
        cur.execute("UPDATE tagall_sessions SET is_active = 0 WHERE group_id = ?", (group_id,))
        _db.commit()

def is_session_active(group_id: int) -> bool:
    with _db_lock:
        cur = _db.cursor()
        cur.execute("SELECT is_active FROM tagall_sessions WHERE group_id = ?", (group_id,))
        r = cur.fetchone()
        return bool(r[0]) if r else False

# =========================================================
# LIVEGRAM MESSAGE MAPPING
# =========================================================

def save_message_map(admin_msg_id: int, user_id: int):
    """Simpan hubungan: pesan admin -> user"""
    with _db_lock:
        cur = _db.cursor()
        cur.execute(
            "REPLACE INTO livegram_map (admin_msg_id, user_id) VALUES (?, ?)",
            (admin_msg_id, user_id)
        )
        _db.commit()

def get_user_by_admin_message(admin_msg_id: int) -> Optional[int]:
    """Ambil user_id berdasarkan pesan admin"""
    with _db_lock:
        cur = _db.cursor()
        cur.execute(
            "SELECT user_id FROM livegram_map WHERE admin_msg_id = ?",
            (admin_msg_id,)
        )
        row = cur.fetchone()
        return row[0] if row else None
