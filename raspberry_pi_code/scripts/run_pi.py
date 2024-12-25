import time
from raspberry_pi_code.data_collection_layer.data_collector import collect_and_store_data
from raspberry_pi_code.local_database.database_manager import initialize_database, delete_old_records
from raspberry_pi_code.configs.config_manager import get_collection_interval
from raspberry_pi_code.errors import delete_old_logs

def main():
    
    initialize_database()
    interval = get_collection_interval()

    while True:
        try:
            
            collect_and_store_data()
            delete_old_records(days=180)
            delete_old_logs(retention_days=180)
            print(f"Waiting for {interval} seconds before the next collection...")
        except Exception as e:
            print(f"Error during data collection: {e}")       
        time.sleep(interval)


if __name__ == "__main__":
    main()
