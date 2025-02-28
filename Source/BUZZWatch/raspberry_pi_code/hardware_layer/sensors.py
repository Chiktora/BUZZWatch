# sensors.py (Using RPi.GPIO and adafruit-circuitpython-dht)

import time
import RPi.GPIO as GPIO
import board
import adafruit_dht
import json
import os
from hx711 import HX711  # Updated import
from BUZZWatch.raspberry_pi_code.errors import log_error_to_file
from BUZZWatch.raspberry_pi_code.config import (
    INDOOR_DHT22_PIN,
    OUTDOOR_DHT22_PIN,
    HX711_DOUT_PIN,
    HX711_SCK_PIN
)

# Define path for calibration data
CALIBRATION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'hx711_calibration.json')

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --------------------------------------------------------
# DHT22 (Using CircuitPython) - Indoor and Outdoor sensors
# --------------------------------------------------------
try:
    # Initialize DHT22 sensors
    dht22_indoor = adafruit_dht.DHT22(getattr(board, f'D{INDOOR_DHT22_PIN}'))
    dht22_outdoor = adafruit_dht.DHT22(getattr(board, f'D{OUTDOOR_DHT22_PIN}'))
    print(f"DHT22 sensors configured: Indoor(GPIO{INDOOR_DHT22_PIN}), Outdoor(GPIO{OUTDOOR_DHT22_PIN})")
except Exception as e:
    dht22_indoor = None
    dht22_outdoor = None
    log_error_to_file("ERR_DHT22_INIT", str(e))
    print(f"Error initializing DHT22 sensors: {str(e)}")

# --------------------------------------------------------
# HX711 - Weight Sensor
# --------------------------------------------------------
try:
    # Initialize HX711
    hx = HX711(dout_pin=HX711_DOUT_PIN, pd_sck_pin=HX711_SCK_PIN)
    
    # Reset scale
    hx.reset()
    
    # Configure channel and gain for load cells
    hx.channel = 'A'  # Most load cell setups use channel A
    hx.channel_a_gain = 128  # Common gain setting for load cells
    
    # Reference value for calibration - will be loaded from file if available
    REFERENCE_UNIT = 1  # Default value
    ZERO_OFFSET = 0  # Default zero offset
    
    # Load calibration data if exists
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, 'r') as f:
                calibration_data = json.load(f)
                REFERENCE_UNIT = calibration_data.get('reference_unit', 1)
                ZERO_OFFSET = calibration_data.get('zero_offset', 0)
                print(f"Loaded HX711 calibration: reference_unit={REFERENCE_UNIT}, zero_offset={ZERO_OFFSET}")
        except Exception as e:
            log_error_to_file("ERR_HX711_CALIBRATION_LOAD", str(e))
            print(f"Error loading HX711 calibration: {str(e)}")
    else:
        print("No HX711 calibration file found. Using default values.")
    
    print(f"HX711 sensor initialized: DOUT(GPIO{HX711_DOUT_PIN}), SCK(GPIO{HX711_SCK_PIN})")
except Exception as e:
    hx = None
    log_error_to_file("ERR_HX711_INIT", str(e))
    print(f"Error initializing HX711 sensor: {str(e)}")

# --------------------------------------------------------
# Calibration Functions
# --------------------------------------------------------
def calibrate_hx711(known_weight_value):
    """
    Calibrate the HX711 sensor with a known weight.
    Saves calibration data to a JSON file.
    
    Args:
        known_weight_value: The known weight value in your preferred units (e.g., grams)
        
    Returns:
        tuple: (success, message)
    """
    global REFERENCE_UNIT, ZERO_OFFSET
    
    if not hx:
        return False, "HX711 not initialized"
    
    try:
        # Step 1: Get zero reading (tare)
        print("Measuring zero weight... please ensure scale is empty")
        zero_readings = []
        for _ in range(10):
            try:
                readings = hx.get_raw_data(times=5)
                if readings:
                    zero_readings.extend(readings)
            except Exception as e:
                print(f"Error during zero reading: {e}")
            time.sleep(0.1)
        
        if not zero_readings:
            return False, "Failed to get zero readings"
        
        # Calculate average zero reading (after removing outliers)
        zero_readings.sort()
        if len(zero_readings) > 4:
            # Remove extreme values
            zero_readings = zero_readings[2:-2]
        zero_offset = sum(zero_readings) / len(zero_readings)
        
        # Step 2: Get reading with known weight
        print(f"Please place a known weight of {known_weight_value} on the scale")
        time.sleep(2)  # Give user time to place the weight
        print("Measuring weight...")
        
        weight_readings = []
        for _ in range(10):
            try:
                readings = hx.get_raw_data(times=5)
                if readings:
                    weight_readings.extend(readings)
            except Exception as e:
                print(f"Error during weight reading: {e}")
            time.sleep(0.1)
        
        if not weight_readings:
            return False, "Failed to get weight readings"
        
        # Calculate average weight reading (after removing outliers)
        weight_readings.sort()
        if len(weight_readings) > 4:
            # Remove extreme values
            weight_readings = weight_readings[2:-2]
        weight_value = sum(weight_readings) / len(weight_readings)
        
        # Calculate reference unit
        reference_unit = (weight_value - zero_offset) / known_weight_value
        
        # Update global values
        ZERO_OFFSET = zero_offset
        REFERENCE_UNIT = reference_unit
        
        # Save calibration to file
        calibration_data = {
            'reference_unit': reference_unit,
            'zero_offset': zero_offset,
            'calibration_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'known_weight_used': known_weight_value
        }
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(CALIBRATION_FILE), exist_ok=True)
        
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(calibration_data, f, indent=4)
        
        return True, f"Calibration successful. Reference unit: {reference_unit:.2f}, Zero offset: {zero_offset:.2f}"
    
    except Exception as e:
        error_msg = f"Calibration error: {str(e)}"
        log_error_to_file("ERR_HX711_CALIBRATION", error_msg)
        return False, error_msg

def is_calibrated():
    """Check if the HX711 sensor has been calibrated."""
    return os.path.exists(CALIBRATION_FILE)

# --------------------------------------------------------
# DHT22 Read Functions
# --------------------------------------------------------
def read_dht22_indoor():
    """
    Uses CircuitPython to read temperature/humidity from the indoor sensor.
    Attempts 5 readings with 100ms intervals, averages successful readings.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht22_indoor:
        return None, None
        
    successful_temps = []
    successful_humids = []
    
    for _ in range(5):  # Try 5 times
        try:
            temperature = dht22_indoor.temperature
            humidity = dht22_indoor.humidity
            
            if temperature is not None and humidity is not None:
                successful_temps.append(temperature)
                successful_humids.append(humidity)
            
            time.sleep(0.1)  # 100ms delay between readings
            
        except RuntimeError as e:
            # DHT22 sometimes fails to read, this is normal
            continue
        except Exception as e:
            log_error_to_file("ERR_DHT22_INDOOR", str(e))
            continue
    
    # If we have any successful readings, return their average
    if successful_temps and successful_humids:
        avg_temp = round(sum(successful_temps) / len(successful_temps), 1)
        avg_humid = round(sum(successful_humids) / len(successful_humids), 1)
        return avg_temp, avg_humid
    else:
        log_error_to_file("ERR_DHT22_INDOOR", "No valid readings after 5 attempts")
        return None, None

def read_dht22_outdoor():
    """
    Uses CircuitPython to read temperature/humidity from the outdoor sensor.
    Attempts 5 readings with 100ms intervals, averages successful readings.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht22_outdoor:
        return None, None
        
    successful_temps = []
    successful_humids = []
    
    for _ in range(5):  # Try 5 times
        try:
            temperature = dht22_outdoor.temperature
            humidity = dht22_outdoor.humidity
            
            if temperature is not None and humidity is not None:
                successful_temps.append(temperature)
                successful_humids.append(humidity)
            
            time.sleep(0.1)  # 100ms delay between readings
            
        except RuntimeError as e:
            # DHT22 sometimes fails to read, this is normal
            continue
        except Exception as e:
            log_error_to_file("ERR_DHT22_OUTDOOR", str(e))
            continue
    
    # If we have any successful readings, return their average
    if successful_temps and successful_humids:
        avg_temp = round(sum(successful_temps) / len(successful_temps), 1)
        avg_humid = round(sum(successful_humids) / len(successful_humids), 1)
        return avg_temp, avg_humid
    else:
        log_error_to_file("ERR_DHT22_OUTDOOR", "No valid readings after 5 attempts")
        return None, None

# --------------------------------------------------------
# HX711 (Weight) Read Function
# --------------------------------------------------------
def read_weight(return_kg=True):
    """
    Read weight from HX711 sensor with 4 load cells.
    Gets multiple raw readings with timeout protection, filters outliers, 
    and averages remaining values.
    Applies calibration factor to convert to actual weight.
    
    Args:
        return_kg: If True, returns weight in kilograms, otherwise in grams
        
    Returns:
        Weight value (in kg if return_kg=True, in g if return_kg=False) or None on error.
    """
    if not hx:
        return None
    
    try:
        # Add timeout protection for get_raw_data
        import threading
        import queue

        result_queue = queue.Queue()
        
        def read_with_timeout():
            try:
                # Attempt to get raw data
                readings = hx.get_raw_data(times=5)  # Reduced from 10 to 5 for faster reading
                result_queue.put(("success", readings))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # Start reading in a separate thread
        read_thread = threading.Thread(target=read_with_timeout)
        read_thread.daemon = True
        read_thread.start()
        
        # Wait for the thread to complete or timeout
        read_thread.join(timeout=3.0)  # 3 second timeout
        
        if read_thread.is_alive():
            # If the thread is still alive after timeout, it's stuck
            log_error_to_file("ERR_WEIGHT", "Reading from HX711 timed out after 3 seconds")
            # We can't kill the thread in Python, but we can continue
            return None
        
        # Check if we have results
        if result_queue.empty():
            log_error_to_file("ERR_WEIGHT", "No data returned from HX711")
            return None
        
        status, raw_readings = result_queue.get()
        
        if status == "error":
            log_error_to_file("ERR_WEIGHT", f"Error reading from HX711: {raw_readings}")
            return None
        
        if not raw_readings or len(raw_readings) == 0:
            log_error_to_file("ERR_WEIGHT", "No valid readings obtained")
            return None
            
        # Filter out outliers if we have enough readings
        if len(raw_readings) >= 3:
            # Sort the readings
            raw_readings.sort()
            # Remove the highest and lowest values
            filtered_readings = raw_readings[1:-1]
        else:
            filtered_readings = raw_readings
        
        # Calculate average of filtered readings
        avg_raw_value = sum(filtered_readings) / len(filtered_readings)
        
        # Apply calibration factor to get actual weight
        # Subtract zero offset first, then divide by reference unit
        weight_g = (avg_raw_value - ZERO_OFFSET) / REFERENCE_UNIT if REFERENCE_UNIT != 0 else 0
        
        # Convert to kg if requested (with exactly 2 decimal places)
        if return_kg:
            return round(weight_g / 1000, 2)  # Convert to kg with 2 decimal places
        else:
            return round(weight_g, 2)  # Keep in grams with 2 decimal places
        
    except Exception as e:
        log_error_to_file("ERR_WEIGHT", f"Unexpected error in read_weight: {str(e)}")
        return None

def read_weight_for_thingspeak():
    """
    Read weight specifically formatted for ThingSpeak - always in kg with 2 decimal places.
    This is a convenience function for the ThingSpeak integration.
    
    Returns:
        Weight in kilograms with 2 decimal places or None on error
    """
    weight_kg = read_weight(return_kg=True)
    
    # Ensure we have exactly 2 decimal places for ThingSpeak
    if weight_kg is not None:
        # Format as string with 2 decimal places, then convert back to float
        # This ensures we have exactly 2 decimal places, not more or less
        weight_kg = float(f"{weight_kg:.2f}")
    
    return weight_kg

def cleanup():
    """
    Clean up GPIO resources
    """
    try:
        if dht22_indoor:
            dht22_indoor.exit()
        if dht22_outdoor:
            dht22_outdoor.exit()
        GPIO.cleanup()
    except:
        pass
