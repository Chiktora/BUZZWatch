from raspberry_pi_code.hardware_layer.sensors import read_sensors
from raspberry_pi_code.hardware_layer.camera import Camera
from raspberry_pi_code.local_database.database_manager import insert_sensor_data, get_unsynced_data, mark_as_synced
from raspberry_pi_code.errors import log_error_to_file
import requests
import json

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
        log_error_to_file("SERVER_URL_ERROR", f"Failed to load server URL: {e}")
        return None

def upload_data_to_server(data, server_url):
    """
    Uploads data to the server.

    Args:
        data (dict): The data to upload.
        server_url (str): The server URL.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        response = requests.post(server_url, json=data, timeout=10)  # Added timeout to prevent hanging
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def sync_unsynced_data(server_url):
    """
    Syncs unsynced data with the server.

    Args:
        server_url (str): The server URL.
    """
    unsynced_data = get_unsynced_data()

    if not unsynced_data:
        print("No unsynced data to process.")
        return

    for record in unsynced_data:
        record_id = record[0]  # Assuming the first column is the ID
        data = {
            "gas_level": record[2],
            "sound_level": record[3],
            "weight": record[4],
            "temp_inside": record[5],
            "temp_outside": record[6],
            "humidity_inside": record[7],
            "humidity_outside": record[8],
            "pressure": record[9],
            "image_path": record[10],
            "timestamp": record[1]
        }

        if upload_data_to_server(data, server_url):
            mark_as_synced(record_id)

def collect_and_store_data():
    server_url = load_server_url()
    if not server_url:
        log_error_to_file("SERVER_URL_ERROR", "Server URL is not configured in pi_settings.json and no default is provided.")
        print("Error: Server URL is not configured.")
        

    camera = Camera()
    if camera.camera is None:
        print("Warning: Camera initialization failed. Proceeding with data collection without capturing images.")
        log_error_to_file("CAM_INIT_FAIL", "Camera initialization failed.")
        camera = None

    try:
        # Read sensor data
        sensor_data = read_sensors()

        # Initialize default values for missing data and update sensor_data directly
        default_sensor_data = {
            "gas_level": None,
            "sound_level": None,
            "weight": None,
            "temp_inside": None,
            "temp_outside": None,
            "humidity_inside": None,
            "humidity_outside": None,
            "pressure": None
        }

        sensor_data = {
            key: sensor_data.get(key, default_value)
            for key, default_value in default_sensor_data.items()
        }

        # Replace missing or invalid sensor data with null values
        for key, value in sensor_data.items():
            if value is None:
                print(f"Warning: Missing or invalid data for sensor: {key}, setting value to None.")
                log_error_to_file(f"SENSOR_{key.upper()}_MISSING", f"Missing or invalid data for sensor: {key}.")

        # Capture an image if the camera is available
        image_path = None
        if camera is not None:
            image_path = camera.capture_image("/home/pi/BUZZWatch/captured_images")
            if not image_path:
                print("Error: Failed to capture image. Using 'None' for image_path.")
                log_error_to_file("IMAGE_CAPTURE_FAIL", "Failed to capture image.")

        # Validate data before inserting into the database
        if any(value is not None for value in sensor_data.values()) or image_path is not None:
            insert_sensor_data(
                gas_level=sensor_data['gas_level'],
                sound_level=sensor_data['sound_level'],
                weight=sensor_data['weight'],
                temp_inside=sensor_data['temp_inside'],
                temp_outside=sensor_data['temp_outside'],
                humidity_inside=sensor_data['humidity_inside'],
                humidity_outside=sensor_data['humidity_outside'],
                pressure=sensor_data['pressure'],
                image_path=image_path,
                synced=0  # Not synced yet
            )
            print("Data successfully collected and stored.")
        else:
            print("Error: Insufficient valid data to insert into the database.")
            log_error_to_file("DATA_VALIDATION_FAIL", "Insufficient valid data to insert into the database.")

        # Sync unsynced data if the server is reachable
        sync_unsynced_data(server_url)

    except Exception as e:
        print(f"Error during data collection: {e}")
        log_error_to_file("DATA_COLLECTION_EXCEPTION", str(e))

    finally:
        # Ensure camera is always released if initialized
        try:
            if camera is not None:
                camera.release_camera()
        except Exception as e:
            print(f"Error releasing camera: {e}")
            log_error_to_file("CAMERA_RELEASE_ERROR", str(e))
