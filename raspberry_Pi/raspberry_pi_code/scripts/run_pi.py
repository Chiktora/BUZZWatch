import time
import requests
from raspberry_pi_code.data_collection_layer.data_collector import collect_and_store_data
from raspberry_pi_code.local_database.database_manager import initialize_database, delete_old_records
from raspberry_pi_code.services.api.calibration_api import load_calibration_data
from raspberry_pi_code.errors import delete_old_logs, log_error_to_file
from raspberry_pi_code.utils.system_utils import get_system_state, validate_interval

def fetch_collection_interval():
    """
    Fetches the data collection interval from the API.
    Returns a default value of 300 seconds if the API call fails.
    """
    default_interval = 300
    try:
        response = requests.get("http://<raspberry_pi_ip>:5000/get_interval", timeout=10)
        if response.status_code == 200:
            interval = response.json().get("collection_interval", default_interval)
            print(f"Collection interval retrieved: {interval} seconds.")
            return interval
        else:
            print("Error retrieving collection interval. Using default value.")
            return default_interval
    except requests.RequestException as e:
        print(f"Failed to fetch collection interval: {e}. Using default value.")
        log_error_to_file("FETCH_INTERVAL_ERROR", str(e))
        return default_interval

def main():
    """
    Main process for data collection, cleaning old records, and logs.
    """
    try:
        print("Initializing database...")
        try:
            initialize_database()
        except Exception as db_error:
            system_state = get_system_state()
            error_message = f"Database initialization failed: {db_error}. System state: {system_state}"
            print(error_message)
            log_error_to_file("DATABASE_INIT_ERROR", error_message)
            raise

        print("Loading data collection interval...")
        interval = fetch_collection_interval()
        interval = validate_interval(interval)

        print("Loading calibration data...")
        calibration_data = None
        try:
            calibration_data = load_calibration_data()
            if calibration_data:
                print(f"Calibration data loaded: {calibration_data}")
            else:
                print("No calibration data found.")
        except Exception as cal_error:
            system_state = get_system_state()
            error_message = f"Failed to load calibration data: {cal_error}. System state: {system_state}"
            print(error_message)
            log_error_to_file("CALIBRATION_LOAD_ERROR", error_message)

        while True:
            try:
                print("Collecting and storing data...")
                collect_and_store_data()

                print("Deleting old records...")
                delete_old_records(days=180)

                print("Deleting old logs...")
                delete_old_logs(retention_days=180)

                print(f"Waiting for {interval} seconds before the next collection...")
            except Exception as inner_e:
                error_message = f"Error during data collection: {inner_e}"
                print(error_message)
                log_error_to_file("DATA_COLLECTION_ERROR", error_message)
            time.sleep(interval)
    except Exception as e:
        system_state = get_system_state()
        error_message = f"Critical error during initialization: {e}. System state: {system_state}"
        print(error_message)
        log_error_to_file("INITIALIZATION_ERROR", error_message)

if __name__ == "__main__":
    main()
