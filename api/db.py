import sqlite3
import os
import sys
from typing import List, Dict, Any, Optional

# Add project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(project_root, 'results', 'analytics.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def list_runs_summary() -> List[Dict[str, Any]]:
    """
    Returns a lightweight summary of all runs for the list view.
    """
    if not os.path.exists(DB_PATH):
        return []

    query = """
    SELECT r.run_id, r.timestamp, r.status, m.max_temperature, m.stability_ratio
    FROM runs r
    LEFT JOIN metrics m ON r.run_id = m.run_id
    ORDER BY r.timestamp DESC
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def get_run_details(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Get generic run metadata.
    """
    if not os.path.exists(DB_PATH):
        return None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None
