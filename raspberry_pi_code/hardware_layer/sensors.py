# sensors.py (Redacted & Using CircuitPython DHT)

import time
import board
import adafruit_dht
from hx711 import HX711
from raspberry_pi_code.errors import log_error_to_file

# --------------------------------------------------------
# DHT22 (CircuitPython) - Indoor on board.D4, Outdoor on board.D17
# --------------------------------------------------------
try:
    dht_indoor = adafruit_dht.DHT22(board.D4)     # BCM GPIO4
    dht_outdoor = adafruit_dht.DHT22(board.D17)   # BCM GPIO17
except Exception as e:
    dht_indoor = None
    dht_outdoor = None
    log_error_to_file("ERR_DHT_INIT", str(e))

# --------------------------------------------------------
# HX711 - Weight Sensor
# --------------------------------------------------------
HX711_DOUT_GPIO = 5
HX711_PD_SCK_GPIO = 6
try:
    hx = HX711(dout_pin=HX711_DOUT_GPIO, pd_sck_pin=HX711_PD_SCK_GPIO)
    hx.set_scale_ratio(1)  # No calibration
    hx.tare()
except Exception as e:
    hx = None
    log_error_to_file("ERR_HX711_INIT", str(e))

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
