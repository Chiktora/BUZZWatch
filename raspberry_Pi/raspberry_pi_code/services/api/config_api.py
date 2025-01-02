from flask import Blueprint, request, jsonify
import json
from raspberry_pi_code.errors import log_error_to_file

# Path to the configuration file
CONFIG_FILE = "/home/pi/BUZZWatch/raspberry_pi_code/configs/config.json"

config_api = Blueprint("config_api", __name__)

@config_api.route('/get_interval', methods=['GET'])
def get_collection_interval():
    """
    Reads the data collection interval from the config.json file.
    Returns a default value of 300 seconds if not found or if an error occurs.
    """
    default_interval = 300  # Default interval is 300 seconds
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            interval = config.get("collection_interval", default_interval)

            # Validate the interval
            if isinstance(interval, int) and interval > 0:
                print(f"Valid collection interval retrieved: {interval} seconds.")
                return jsonify({"collection_interval": interval}), 200
            else:
                error_message = "Invalid or missing collection interval in config.json"
                print(error_message)
                log_error_to_file("INVALID_COLLECTION_INTERVAL", error_message)
                return jsonify({"error": error_message}), 400
    except Exception as e:
        error_message = f"Error reading configuration: {e}"
        print(error_message)
        log_error_to_file("CONFIG_READ_ERROR", error_message)
        return jsonify({"error": error_message}), 500

@config_api.route('/update_interval', methods=['POST'])
def update_collection_interval():
    """
    API endpoint to update the data collection interval.
    """
    try:
        data = request.json
        new_interval = data.get("collection_interval")

        if not isinstance(new_interval, int) or new_interval <= 0:
            error_message = "Invalid interval provided. Must be a positive integer."
            print(error_message)
            log_error_to_file("INVALID_INTERVAL_UPDATE", error_message)
            return jsonify({"status": "error", "message": error_message}), 400

        # Read the existing configuration
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Update the interval
        config["collection_interval"] = new_interval

        # Save the updated configuration
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        print(f"Collection interval updated to {new_interval} seconds.")
        return jsonify({"status": "success", "message": f"Interval updated to {new_interval} seconds."}), 200

    except Exception as e:
        error_message = f"Failed to update collection interval: {e}"
        print(error_message)
        log_error_to_file("UPDATE_INTERVAL_ERROR", error_message)
        return jsonify({"status": "error", "message": error_message}), 500
