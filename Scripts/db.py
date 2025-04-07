import sqlite3
import os

# Dynamically set the path to the SQLite DB file
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/cowrie_events.db')


def init_db():
    """Create the events table if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                src_ip TEXT,
                username TEXT,
                password TEXT,
                commands TEXT,
                is_anomaly INTEGER,
                source TEXT DEFAULT 'cowrie'
            );
        ''')
        conn.commit()


def insert_event(timestamp, src_ip, username, password, commands, is_anomaly, source="cowrie"):
    """Insert a new honeypot event (from Cowrie or OpenCanary) into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (timestamp, src_ip, username, password, commands, is_anomaly, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, src_ip, username, password, commands, int(is_anomaly), source))
        conn.commit()


def get_recent_events(limit=50):
    """Fetch the most recent honeypot events."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, src_ip, username, password, commands, is_anomaly, source
            FROM events
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()


def clear_old_events(max_records=1000):
    """Auto-trim the database to avoid bloat."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        total_rows = cursor.fetchone()[0]

        if total_rows > max_records:
            delete_count = total_rows - max_records
            cursor.execute(
                f"DELETE FROM events WHERE id IN (SELECT id FROM events ORDER BY id ASC LIMIT {delete_count})")
            conn.commit()
            print(f"[INFO] Deleted {delete_count} old events to keep max at {max_records}.")

# Initialize the database on first run
init_db()
