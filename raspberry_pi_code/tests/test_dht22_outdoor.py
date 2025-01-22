#!/usr/bin/env python3

import time
from raspberry_pi_code.hardware_layer.sensors import read_dht22_outdoor

def test_outdoor_dht22():
    print("\nTesting Outdoor DHT22 Sensor (GPIO17):")
    print("-" * 30)
    
    # Read sensor data
    temp, humidity = read_dht22_outdoor()
    
    # Check if reading was successful
    if temp is None or humidity is None:
        print("ERROR: Could not read from outdoor DHT22!")
        return False
    
    # Display readings
    print(f"Temperature: {temp}°C")
    print(f"Humidity: {humidity}%")
    
    # Validate readings are in reasonable range
    if not (-40 <= temp <= 80):
        print("ERROR: Temperature reading out of range (-40°C to 80°C)!")
        return False
        
    if not (0 <= humidity <= 100):
        print("ERROR: Humidity reading out of range (0% to 100%)!")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_outdoor_dht22()
        if success:
            print("\nOutdoor DHT22 test passed!")
            exit(0)
        else:
            print("\nOutdoor DHT22 test failed!")
            exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during test: {str(e)}")
        exit(1) 