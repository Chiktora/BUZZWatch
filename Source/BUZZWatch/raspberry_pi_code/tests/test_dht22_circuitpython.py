#!/usr/bin/env python3

import time
import board
import adafruit_dht
import platform
import os

def print_system_info():
    print("\nSystem Information:")
    print("=" * 40)
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python version: {platform.python_version()}")
    
    # Check GPIO permissions
    gpio_group = os.system('groups | grep -q gpio')
    print(f"User in GPIO group: {'Yes' if gpio_group == 0 else 'No'}")
    
    # Check if GPIO4 is exported
    gpio4_exists = os.path.exists('/sys/class/gpio/gpio4')
    print(f"GPIO4 exported: {'Yes' if gpio4_exists else 'No'}")
    print("=" * 40)

def test_dht22_basic():
    print("\nInitializing sensor...")
    
    # Initial delay to stabilize sensor
    time.sleep(1)
    
    try:
        # Create the sensor object
        # For GPIO4, use board.D4
        dht = adafruit_dht.DHT22(board.D4)
        print("Sensor initialized successfully")
        
        print("\nBasic DHT22 Sensor Test")
        print("=" * 40)
        print("Press CTRL+C to exit")
        print("\nReading sensor data...")
        
        failed_reads = 0
        max_failed_reads = 5
        
        while True:
            try:
                # Get sensor readings
                temperature = dht.temperature
                humidity = dht.humidity
                
                if temperature is not None and humidity is not None:
                    print(f"\nTime: {time.strftime('%H:%M:%S')}")
                    print(f"Temperature: {temperature:.1f}°C")
                    print(f"Humidity: {humidity:.1f}%")
                    print("-" * 40)
                    # Reset failed reads counter on successful read
                    failed_reads = 0
                else:
                    print("Got null readings from sensor")
                    failed_reads += 1
                
            except RuntimeError as e:
                print(f"\nTime: {time.strftime('%H:%M:%S')}")
                print(f"Reading error: {e}")
                failed_reads += 1
                
            except Exception as e:
                print(f"\nTime: {time.strftime('%H:%M:%S')}")
                print(f"Unexpected error: {str(e)}")
                failed_reads += 1
            
            # Check if we've had too many failed reads
            if failed_reads >= max_failed_reads:
                print("\nToo many failed reads. Please check:")
                print("1. Power supply voltage (3.3V or 5V)")
                print("2. Data pin connection (GPIO4)")
                print("3. Pull-up resistor (4.7kΩ-10kΩ)")
                print("4. Ground connection")
                print("\nRestarting sensor...")
                dht.exit()
                time.sleep(2)
                dht = adafruit_dht.DHT22(board.D4)
                failed_reads = 0
            
            # DHT22 requires at least 2 seconds between readings
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        # Always clean up the GPIO resources
        try:
            dht.exit()
        except:
            pass

if __name__ == "__main__":
    print("\nDHT22 Sensor Hardware Test (CircuitPython)")
    print_system_info()
    print("\nThis test will continuously read from the sensor.")
    print("Using GPIO4 (Physical pin 7)")
    print("\nMake sure your connections are:")
    print("1. DHT22 VCC -> 3.3V or 5V")
    print("2. DHT22 DATA -> GPIO4")
    print("3. DHT22 GND -> GND")
    print("4. 4.7K-10K resistor between VCC and DATA (pull-up)")
    
    input("\nPress Enter to start the test (CTRL+C to exit)...")
    test_dht22_basic() 