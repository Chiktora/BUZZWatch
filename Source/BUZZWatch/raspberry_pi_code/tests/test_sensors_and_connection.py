#!/usr/bin/env python3

import os
import time
from raspberry_pi_code.hardware_layer.sensors import (
    read_dht22_indoor,
    read_dht22_outdoor,
    read_weight
)
from raspberry_pi_code.services.api.thingspeak import ThingSpeakAPI

def test_thingspeak_connection():
    """Test ThingSpeak connection"""
    print("\n1. Testing ThingSpeak Connection:")
    print("-" * 30)
    
    api_key = os.getenv('THINGSPEAK_API_KEY')
    if not api_key:
        print("ERROR: ThingSpeak API key not found in environment variables!")
        print("Please set THINGSPEAK_API_KEY environment variable.")
        return False
        
    api = ThingSpeakAPI(api_key)
    return api.test_connection()

def test_indoor_dht22():
    """Test indoor DHT22 sensor"""
    print("\n2. Testing Indoor DHT22 Sensor:")
    print("-" * 30)
    
    temp, humidity = read_dht22_indoor()
    if temp is None or humidity is None:
        print("ERROR: Could not read from indoor DHT22!")
        return False
        
    print(f"Temperature: {temp}°C")
    print(f"Humidity: {humidity}%")
    return True

def test_outdoor_dht22():
    """Test outdoor DHT22 sensor"""
    print("\n3. Testing Outdoor DHT22 Sensor:")
    print("-" * 30)
    
    temp, humidity = read_dht22_outdoor()
    if temp is None or humidity is None:
        print("ERROR: Could not read from outdoor DHT22!")
        return False
        
    print(f"Temperature: {temp}°C")
    print(f"Humidity: {humidity}%")
    return True

def test_weight_sensor():
    """Test HX711 weight sensor"""
    print("\n4. Testing HX711 Weight Sensor:")
    print("-" * 30)
    
    weight = read_weight()
    if weight is None:
        print("ERROR: Could not read from HX711!")
        return False
        
    print(f"Weight: {weight}")
    return True

def run_all_tests():
    """Run all tests and return overall status"""
    print("Starting BUZZWatch System Tests")
    print("=" * 50)
    
    results = {
        "ThingSpeak Connection": test_thingspeak_connection(),
        "Indoor DHT22": test_indoor_dht22(),
        "Outdoor DHT22": test_outdoor_dht22(),
        "Weight Sensor": test_weight_sensor()
    }
    
    print("\nTest Summary:")
    print("=" * 50)
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    try:
        success = run_all_tests()
        if success:
            print("\nAll tests passed successfully!")
            exit(0)
        else:
            print("\nSome tests failed. Please check the errors above.")
            exit(1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during tests: {str(e)}")
        exit(1) 