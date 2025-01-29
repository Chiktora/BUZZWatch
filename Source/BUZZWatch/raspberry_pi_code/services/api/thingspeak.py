import requests
from typing import Optional, Dict, Any
from BUZZWatch.raspberry_pi_code.errors import log_error_to_file

class ThingSpeakAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.thingspeak.com/update"
        
    def test_connection(self) -> bool:
        """
        Test the connection to ThingSpeak by sending a test value.
        Returns True if successful, False if connection fails.
        """
        try:
            print("Testing connection to ThingSpeak...")
            # Send a test value to field 1
            test_data = {
                'api_key': self.api_key,
                'field1': 0  # Test value
            }
            
            response = requests.post(self.base_url, data=test_data)
            
            if response.status_code == 200:
                print("Successfully connected to ThingSpeak!")
                return True
            else:
                print(f"Error connecting to ThingSpeak. Error code: {response.status_code}")
                log_error_to_file("ERR_THINGSPEAK_TEST", 
                                f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error connecting to ThingSpeak: {str(e)}")
            log_error_to_file("ERR_THINGSPEAK_TEST", str(e))
            return False
        
    def upload_data(self, 
                   indoor_temp: Optional[float] = None,
                   indoor_humidity: Optional[float] = None,
                   outdoor_temp: Optional[float] = None,
                   outdoor_humidity: Optional[float] = None,
                   weight: Optional[float] = None) -> bool:
        """
        Upload sensor data to ThingSpeak.
        Returns True if successful, False otherwise.
        
        Field mappings:
        - field1: Indoor Temperature
        - field2: Indoor Humidity
        - field3: Outdoor Temperature
        - field4: Outdoor Humidity
        - field5: Weight
        """
        data: Dict[str, Any] = {
            'api_key': self.api_key
        }
        
        # Add available sensor data
        if indoor_temp is not None:
            data['field1'] = indoor_temp
        if indoor_humidity is not None:
            data['field2'] = indoor_humidity
        if outdoor_temp is not None:
            data['field3'] = outdoor_temp
        if outdoor_humidity is not None:
            data['field4'] = outdoor_humidity
        if weight is not None:
            data['field5'] = weight
            
        try:
            response = requests.post(self.base_url, data=data)
            if response.status_code == 200:
                return True
            else:
                log_error_to_file("ERR_THINGSPEAK_UPLOAD", 
                                f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            log_error_to_file("ERR_THINGSPEAK_UPLOAD", str(e))
            return False 