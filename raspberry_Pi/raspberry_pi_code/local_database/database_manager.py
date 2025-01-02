import sqlite3
import datetime
from raspberry_pi_code.errors import log_error_to_file

DB_PATH = "/home/pi/BUZZWatch/sensor_data.db"

def initialize_database(db_path=DB_PATH):
    try:
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
        print("Database initialized successfully!")
    except Exception as e:
        log_error_to_file("DATABASE_INIT_ERROR", f"Failed to initialize database: {e}")
    finally:
        conn.close()

def insert_sensor_data(gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced=0, db_path=DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Validate inputs before inserting
        if not isinstance(gas_level, (float, int)) or not isinstance(sound_level, (float, int)) or \
           not isinstance(weight, (float, int)) or not isinstance(temp_inside, (float, int, type(None))) or \
           not isinstance(temp_outside, (float, int, type(None))) or not isinstance(humidity_inside, (float, int, type(None))) or \
           not isinstance(humidity_outside, (float, int, type(None))) or not isinstance(pressure, (float, int, type(None))):
            log_error_to_file("DATA_VALIDATION_ERROR", "Invalid data types provided for sensor data.")
            return

        cursor.execute("""
        INSERT INTO sensor_data (gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (gas_level, sound_level, weight, temp_inside, temp_outside, humidity_inside, humidity_outside, pressure, image_path, synced))

        conn.commit()
        print("Data inserted successfully!")
    except Exception as e:
        log_error_to_file("DATA_INSERT_ERROR", f"Failed to insert data: {e}")
    finally:
        conn.close()

def fetch_latest_data(limit=10):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        log_error_to_file("FETCH_DATA_ERROR", f"Failed to fetch latest data: {e}")
        return []
    finally:
        conn.close()

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

        print(f"Deleted {deleted_rows} old records older than {days} days.")
    except Exception as e:
        log_error_to_file("DELETE_RECORDS_ERROR", f"Failed to delete old records: {e}")
    finally:
        conn.close()

def get_unsynced_data():
    """
    Retrieves all unsynced data from the database.

    Returns:
        list: List of unsynced records.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sensor_data WHERE synced = 0")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        log_error_to_file("FETCH_UNSYNCED_DATA_ERROR", f"Failed to fetch unsynced data: {e}")
        return []
    finally:
        conn.close()

def mark_as_synced(record_id):
    """
    Marks a record as synced in the database.

    Args:
        record_id (int): The ID of the record to mark as synced.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("UPDATE sensor_data SET synced = 1 WHERE id = ?", (record_id,))
        conn.commit()
        print(f"Record {record_id} marked as synced.")
    except Exception as e:
        log_error_to_file("MARK_SYNCED_ERROR", f"Failed to mark record {record_id} as synced: {e}")
    finally:
        conn.close()
