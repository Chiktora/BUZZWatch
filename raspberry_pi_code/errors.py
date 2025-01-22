# raspberry_pi_code/errors.py

import os
import json
import time

ERROR_LOG_FILE = "/home/pi/BUZZWatch/errors/errors.json"
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)

def log_error_to_file(error_code, error_message):
    """
    Logs an error to a JSON file in the 'errors' directory.

    Args:
        error_code (str): A unique code for the error type.
        error_message (str): Detailed error message.
    """
    error_data = {
        "code": error_code,
        "message": error_message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load existing errors or start fresh
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE, "r") as f:
                errors = json.load(f)
        except json.JSONDecodeError:
            errors = []
    else:
        errors = []

    errors.append(error_data)

    # Write updated list back to disk
    with open(ERROR_LOG_FILE, "w") as f:
        json.dump(errors, f, indent=4)
