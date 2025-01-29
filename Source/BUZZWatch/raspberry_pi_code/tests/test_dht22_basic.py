#!/usr/bin/env python3

import sys
import time
import Adafruit_DHT
import platform

# Basic configuration
DHT_SENSOR = Adafruit_DHT.DHT22
GPIO_PIN = 4  # GPIO4

def print_system_info():
    print("\nSystem Information:")
    print("=" * 40)
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python version: {platform.python_version()}")
    print("=" * 40)

def test_dht22_basic():
    print(f"\nBasic DHT22 Sensor Test on GPIO{GPIO_PIN}")
    print("=" * 40)
    print("Press CTRL+C to exit")
    print("\nReading sensor data...")
    
    try:
        while True:
            # Get sensor reading with retry mechanism
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, GPIO_PIN, retries=3, delay_seconds=1)
            
            if humidity is not None and temperature is not None:
                print(f"\nTime: {time.strftime('%H:%M:%S')}")
                print(f"Temperature: {temperature:.1f}°C")
                print(f"Humidity: {humidity:.1f}%")
                print("-" * 40)
            else:
                print("Failed to get reading. Check wiring!")
            
            # Wait before next reading
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("If you're seeing platform detection errors, try reinstalling the library with:")
        print("python setup.py install --force-pi")

if __name__ == "__main__":
    # Allow GPIO pin to be specified as command line argument
    if len(sys.argv) > 1:
        GPIO_PIN = int(sys.argv[1])
    
    print("\nDHT22 Sensor Hardware Test")
    print_system_info()
    print("\nThis test will continuously read from the sensor.")
    print(f"Using GPIO{GPIO_PIN} (Physical pin {GPIO_PIN + 2})")
    print("\nMake sure your connections are:")
    print("1. DHT22 VCC -> 3.3V or 5V")
    print(f"2. DHT22 DATA -> GPIO{GPIO_PIN}")
    print("3. DHT22 GND -> GND")
    print("4. 4.7K-10K resistor between VCC and DATA (pull-up)")
    
    input("\nPress Enter to start the test (CTRL+C to exit)...")
    test_dht22_basic() 