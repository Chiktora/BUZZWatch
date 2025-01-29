#!/usr/bin/env python3

import time
from BUZZWatch.raspberry_pi_code.hardware_layer.sensors import read_weight

def test_weight_sensor():
    print("\nTesting HX711 Weight Sensor (DOUT: GPIO5, SCK: GPIO6):")
    print("-" * 50)
    
    # Read sensor data
    weight = read_weight()
    
    # Check if reading was successful
    if weight is None:
        print("ERROR: Could not read from HX711!")
        return False
    
    # Display reading
    print(f"Current weight reading: {weight}")
    
    # Take multiple readings to check stability
    print("\nTaking 5 readings to check stability...")
    readings = []
    for i in range(5):
        weight = read_weight()
        if weight is not None:
            readings.append(weight)
        print(f"Reading {i+1}: {weight}")
        time.sleep(1)
    
    # Check if we got enough readings
    if len(readings) < 3:
        print("ERROR: Not enough successful readings!")
        return False
    
    # Check reading stability
    max_diff = max(readings) - min(readings)
    if max_diff > 1.0:  # More than 1 unit variation
        print(f"WARNING: Readings show high variation ({max_diff} units)")
        print("Consider recalibrating the sensor")
    
    return True

if __name__ == "__main__":
    try:
        success = test_weight_sensor()
        if success:
            print("\nHX711 weight sensor test passed!")
            exit(0)
        else:
            print("\nHX711 weight sensor test failed!")
            exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during test: {str(e)}")
        exit(1) 