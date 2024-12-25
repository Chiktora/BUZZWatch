import os
import json
import time
from datetime import datetime, timedelta

ERROR_LOG_FILE = "/home/pi/BUZZWatch/errors/errors.json"
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)

def log_error_to_file(error_code, error_message):
    """
    Logs an error to a JSON file in the errors directory.

    Args:
        error_code (str): A unique code for the error type.
        error_message (str): Detailed error message.
    """
    error_data = {
        "code": error_code,
        "message": error_message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE, "r") as f:
                errors = json.load(f)
        except json.JSONDecodeError:
            errors = []
    else:
        errors = []

    errors.append(error_data)
    with open(ERROR_LOG_FILE, "w") as f:
        json.dump(errors, f, indent=4)

def delete_old_logs(retention_days=180):
    """
    Deletes logs older than the specified retention period.

    Args:
        retention_days (int): The number of days to retain logs.
    """
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE, "r") as f:
                errors = json.load(f)

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            initial_count = len(errors)
            filtered_errors = [
                error for error in errors
                if datetime.strptime(error["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff_date
            ]

            deleted_count = initial_count -len(filtered_errors)

            with open(ERROR_LOG_FILE, "w") as f:
                json.dump(filtered_errors, f, indent=4)

            print(f"Deleted {deleted_count} old errors older than {retention_days} days.")
        except Exception as e:
            log_error_to_file("LOG_CLEANUP_FAIL", f"Failed to clean up old logs: {e}")
