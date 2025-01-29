# sensors.py (Redacted & Using CircuitPython DHT)

import time
import board
import adafruit_dht
from hx711 import HX711
from raspberry_pi_code.errors import log_error_to_file
from raspberry_pi_code.config import (
    INDOOR_DHT22_PIN,
    OUTDOOR_DHT22_PIN,
    HX711_DOUT_PIN,
    HX711_SCK_PIN
)

# --------------------------------------------------------
# DHT22 (CircuitPython) - Indoor and Outdoor sensors
# --------------------------------------------------------
try:
    # Use getattr to dynamically get the correct board pin
    indoor_pin = getattr(board, f'D{INDOOR_DHT22_PIN}')
    outdoor_pin = getattr(board, f'D{OUTDOOR_DHT22_PIN}')
    
    dht_indoor = adafruit_dht.DHT22(indoor_pin)
    dht_outdoor = adafruit_dht.DHT22(outdoor_pin)
    print(f"DHT22 sensors initialized: Indoor(GPIO{INDOOR_DHT22_PIN}), Outdoor(GPIO{OUTDOOR_DHT22_PIN})")
except Exception as e:
    dht_indoor = None
    dht_outdoor = None
    log_error_to_file("ERR_DHT_INIT", str(e))
    print(f"Error initializing DHT22 sensors: {str(e)}")

# --------------------------------------------------------
# HX711 - Weight Sensor
# --------------------------------------------------------
try:
    hx = HX711(dout_pin=HX711_DOUT_PIN, pd_sck_pin=HX711_SCK_PIN)
    hx.set_scale_ratio(1)  # No calibration
    hx.tare()
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
    Uses CircuitPython DHT to read temperature/humidity from the indoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht_indoor:
        return None, None
    try:
        temp_c = dht_indoor.temperature
        hum    = dht_indoor.humidity
        if temp_c is not None and hum is not None:
            return temp_c, hum
        else:
            log_error_to_file("ERR_DHT22_INDOOR", "No valid reading.")
    except Exception as e:
        log_error_to_file("ERR_DHT22_INDOOR", str(e))
    return None, None

def read_dht22_outdoor():
    """
    Uses CircuitPython DHT to read temperature/humidity from the outdoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    if not dht_outdoor:
        return None, None
    try:
        temp_c = dht_outdoor.temperature
        hum    = dht_outdoor.humidity
        if temp_c is not None and hum is not None:
            return temp_c, hum
        else:
            log_error_to_file("ERR_DHT22_OUTDOOR", "No valid reading.")
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
        return hx.get_weight_mean(5)
    except Exception as e:
        log_error_to_file("ERR_WEIGHT", str(e))
        return None
