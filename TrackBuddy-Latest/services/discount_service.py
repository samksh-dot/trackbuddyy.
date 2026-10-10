import sqlite3
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_student_discounts(destination_id=None, category=None):
    """
    Returns authentic verified student concessions for monuments, transit, and hostels.
    """
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM discounts WHERE 1=1"
    params = []

    if destination_id:
        query += " AND (destination_id = ? OR destination_id IS NULL)"
        params.append(destination_id)

    if category:
        query += " AND applicable_category = ?"
        params.append(category)

    query += " ORDER BY is_verified DESC, id ASC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
