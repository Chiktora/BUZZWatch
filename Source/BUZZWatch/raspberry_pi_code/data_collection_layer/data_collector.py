# raspberry_pi_code/data_collection_layer/data_collector.py

import time
from typing import Optional
from datetime import datetime
from raspberry_pi_code.hardware_layer.sensors import (
    read_dht22_indoor,
    read_dht22_outdoor,
    read_weight
)
from raspberry_pi_code.services.api.thingspeak import ThingSpeakAPI
from raspberry_pi_code.errors import log_error_to_file

class DataCollector:
    def __init__(self, thingspeak_api_key: str):
        """Initialize the data collector with ThingSpeak API key."""
        self.thingspeak = ThingSpeakAPI(thingspeak_api_key)
        self.last_weight = None
        self.WEIGHT_DROP_THRESHOLD = 2.0
        
    def collect_and_upload_data(self) -> bool:
        """
        Collect data from all sensors and upload to ThingSpeak.
        Returns True if successful, False if any error occurred.
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] Collecting sensor data...")
            
            # Read indoor DHT22
            indoor_temp, indoor_humidity = read_dht22_indoor()
            print(f"Indoor: {indoor_temp}°C, {indoor_humidity}% RH")
            
            # Read outdoor DHT22
            outdoor_temp, outdoor_humidity = read_dht22_outdoor()
            print(f"Outdoor: {outdoor_temp}°C, {outdoor_humidity}% RH")
            
            # Read weight
            weight = read_weight()
            print(f"Weight: {weight}")
            
            # Store last weight for future comparison
            self.last_weight = weight
            
            # Upload to ThingSpeak
            print("Uploading to ThingSpeak...")
            success = self.thingspeak.upload_data(
                indoor_temp=indoor_temp,
                indoor_humidity=indoor_humidity,
                outdoor_temp=outdoor_temp,
                outdoor_humidity=outdoor_humidity,
                weight=weight
            )
            
            if not success:
                log_error_to_file("ERR_DATA_UPLOAD", "Failed to upload data to ThingSpeak")
                print("Upload failed!")
                return False
            
            print("Upload successful!")    
            return True
            
        except Exception as e:
            log_error_to_file("ERR_DATA_COLLECTION", str(e))
            print(f"Error during data collection: {str(e)}")
            return False


