#!/usr/bin/env python3

import time
import board
import adafruit_dht
from BUZZWatch.raspberry_pi_code.config import INDOOR_DHT22_PIN

def test_indoor_dht22():
    print("\nTesting Indoor DHT22 Sensor (GPIO{0}):".format(INDOOR_DHT22_PIN))
    print("-" * 30)
    
    dht = None
    try:
        # Initialize sensor
        print("Initializing sensor...")
        dht = adafruit_dht.DHT22(getattr(board, f'D{INDOOR_DHT22_PIN}'))
        time.sleep(1)  # Wait for sensor to stabilize
        
        print("Reading sensor data (this may take a few seconds)...")
        
        # Try multiple readings
        for attempt in range(3):
            print(f"\nAttempt {attempt + 1}:")
            
            try:
                # Read sensor data
                temp = dht.temperature
                humidity = dht.humidity
                
                if temp is not None and humidity is not None:
                    print(f"Temperature: {temp:.1f}°C")
                    print(f"Humidity: {humidity:.1f}%")
                    
                    # Validate readings are in reasonable range
                    if not (-40 <= temp <= 80):
                        print("ERROR: Temperature reading out of range (-40°C to 80°C)!")
                        continue
                        
                    if not (0 <= humidity <= 100):
                        print("ERROR: Humidity reading out of range (0% to 100%)!")
                        continue
                        
                    print("\nReading successful!")
                    return True
                else:
                    print("Failed to get reading. Trying again...")
            except RuntimeError as e:
                print(f"Error reading sensor: {e}")
            
            time.sleep(2)
        
        print("\nERROR: Could not get valid reading after 3 attempts!")
        return False
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False
    finally:
        if dht:
            dht.exit()

if __name__ == "__main__":
    try:
        success = test_indoor_dht22()
        if success:
            print("\nIndoor DHT22 test passed!")
            exit(0)
        else:
            print("\nIndoor DHT22 test failed!")
            exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during test: {str(e)}")
        exit(1) 