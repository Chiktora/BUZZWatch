# sensors.py (Using RPi.GPIO and adafruit-circuitpython-dht)

import time
import RPi.GPIO as GPIO
import board
import adafruit_dht
from hx711 import HX711  # Updated import
from BUZZWatch.raspberry_pi_code.errors import log_error_to_file
from BUZZWatch.raspberry_pi_code.config import (
    INDOOR_DHT22_PIN,
    OUTDOOR_DHT22_PIN,
    HX711_DOUT_PIN,
    HX711_SCK_PIN
)

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
    hx = HX711(dout_pin=HX711_DOUT_PIN, sck_pin=HX711_SCK_PIN)
    
    # Reset and tare scale
    hx.reset()
    hx.tare()
    
    # Set scale - you'll need to calibrate this value for your specific setup
    hx.set_scale(1)  # Replace with your calibration value
    
    print(f"HX711 sensor initialized: DOUT(GPIO{HX711_DOUT_PIN}), SCK(GPIO{HX711_SCK_PIN})")
except Exception as e:
    hx = None
    log_error_to_file("ERR_HX711_INIT", str(e))
    print(f"Error initializing HX711 sensor: {str(e)}")

# --------------------------------------------------------
# DHT22 Read Functions
# --------------------------------------------------------
def read_dht22_indoor():
    """
    Uses CircuitPython to read temperature/humidity from the indoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht22_indoor:
        return None, None
        
    try:
        temperature = dht22_indoor.temperature
        humidity = dht22_indoor.humidity
        
        if temperature is not None and humidity is not None:
            # Round to 1 decimal place
            temperature = round(temperature, 1)
            humidity = round(humidity, 1)
            return temperature, humidity
        else:
            log_error_to_file("ERR_DHT22_INDOOR", "No valid reading.")
    except RuntimeError as e:
        # DHT22 sometimes fails to read, this is normal
        log_error_to_file("ERR_DHT22_INDOOR", f"Runtime error: {str(e)}")
    except Exception as e:
        log_error_to_file("ERR_DHT22_INDOOR", str(e))
    return None, None

def read_dht22_outdoor():
    """
    Uses CircuitPython to read temperature/humidity from the outdoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht22_outdoor:
        return None, None
        
    try:
        temperature = dht22_outdoor.temperature
        humidity = dht22_outdoor.humidity
        
        if temperature is not None and humidity is not None:
            # Round to 1 decimal place
            temperature = round(temperature, 1)
            humidity = round(humidity, 1)
            return temperature, humidity
        else:
            log_error_to_file("ERR_DHT22_OUTDOOR", "No valid reading.")
    except RuntimeError as e:
        # DHT22 sometimes fails to read, this is normal
        log_error_to_file("ERR_DHT22_OUTDOOR", f"Runtime error: {str(e)}")
    except Exception as e:
        log_error_to_file("ERR_DHT22_OUTDOOR", str(e))
    return None, None

# --------------------------------------------------------
# HX711 (Weight) Read Function
# --------------------------------------------------------
def read_weight():
    """
    Read weight from HX711 sensor.
    Returns weight value or None on error.
    """
    if not hx:
        return None
    try:
        # Get average of 5 readings
        readings = []
        for _ in range(5):
            readings.append(hx.get_weight())
            time.sleep(0.1)
        
        # Remove any extreme values and average the rest
        readings.sort()
        if len(readings) >= 5:
            readings = readings[1:-1]  # Remove highest and lowest
        
        weight = sum(readings) / len(readings)
        return round(weight, 2)  # Round to 2 decimal places
        
    except Exception as e:
        log_error_to_file("ERR_WEIGHT", str(e))
        return None

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
