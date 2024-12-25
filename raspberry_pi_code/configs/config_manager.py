import json

# Path to the configuration file
CONFIG_FILE = "/home/pi/BUZZWatch/raspberry_pi_code/configs/config.json"

def get_collection_interval():
    """
    Reads the data collection interval from the config.json file.
    Returns a default value of 300 seconds if not found or if an error occurs.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("collection_interval", 300)  # Default interval is 300 seconds
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return 300  # Return default interval on error
