# raspberry_pi_code/scripts/run_pi.py

import time
from raspberry_pi_code.config import THINGSPEAK_API_KEY, COLLECTION_INTERVAL
from raspberry_pi_code.data_collection_layer.data_collector import DataCollector
from raspberry_pi_code.errors import log_error_to_file

def main():
    print("[run_pi] Starting BUZZWatch...")

    # Initialize data collector with API key from config
    collector = DataCollector(THINGSPEAK_API_KEY)
    
    # Test ThingSpeak connection
    if not collector.thingspeak.test_connection():
        print("Program stopped due to ThingSpeak connection issue.")
        return
    
    print("[run_pi] Starting data collection...")
    
    while True:
        try:
            # Collect and upload sensor data
            collector.collect_and_upload_data()
            
            # Wait for next collection interval
            time.sleep(COLLECTION_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nStopping BUZZWatch data collection...")
            break
        except Exception as e:
            log_error_to_file("ERR_MAIN", str(e))
            time.sleep(5)  # Wait a bit before retrying

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error_to_file("ERR_RUN_PI_MAIN", str(e))
        time.sleep(5)
