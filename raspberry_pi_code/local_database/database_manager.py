import sqlite3
import datetime
import json

DB_PATH = "/home/pi/BUZZWatch/sensor_data.db"
SETTINGS_PATH = "/home/pi/BUZZWatch/raspberry_pi_code/configs/pi_settings.json"

def load_server_url():
    """
    Loads the server URL from the pi_settings.json file.

    Returns:
        str: The server URL.
    """
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
        return settings.get("server_url")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading server URL from settings: {e}")
        return None

def initialize_database(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the table structure with new columns for sync status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        gas_level REAL,
        sound_level REAL,
        weight REAL,
        temp_inside REAL,
        temp_outside REAL,
        humidity_inside REAL,
        humidity_outside REAL,
        pressure REAL,
        image_path TEXT,
        synced INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def insert_sensor_data(gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced=0, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Validate inputs before inserting
    if not isinstance(gas_level, (float, int)) or not isinstance(sound_level, (float, int)) or \
       not isinstance(weight, (float, int)) or not isinstance(temp_inside, (float, int, type(None))) or \
       not isinstance(temp_outside, (float, int, type(None))) or not isinstance(humidity_inside, (float, int, type(None))) or \
       not isinstance(humidity_outside, (float, int, type(None))) or not isinstance(pressure, (float, int, type(None))):
        print("Invalid data types provided for sensor data.")
        conn.close()
        return

    cursor.execute("""
    INSERT INTO sensor_data (gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced))

    conn.commit()
    conn.close()
    print("Data inserted successfully!")

def fetch_latest_data(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_old_records(days=180):
    """
    Deletes records older than the specified number of days from the database.

    Args:
        days (int): The age of records to keep. Records older than this will be deleted.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Calculate threshold date
        threshold_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        # Delete records older than the threshold date
        cursor.execute("DELETE FROM sensor_data WHERE timestamp < ?", (threshold_date,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"Deleted {deleted_rows} old records older than {days} days.")
    except Exception as e:
        print(f"Error deleting old records: {e}")

def get_unsynced_data():
    """
    Retrieves all unsynced data from the database.

    Returns:
        list: List of unsynced records.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sensor_data WHERE synced = 0")
    rows = cursor.fetchall()

    conn.close()
    return rows

def mark_as_synced(record_id):
    """
    Marks a record as synced in the database.

    Args:
        record_id (int): The ID of the record to mark as synced.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE sensor_data SET synced = 1 WHERE id = ?", (record_id,))

    conn.commit()
    conn.close()
    print(f"Record {record_id} marked as synced.")
