import random
import json
from smbus2 import SMBus
import adafruit_dht
import board
from raspberry_pi_code.errors import log_error_to_file

CALIBRATION_FILE = "/home/pi/BUZZWatch/raspberry_pi_code/configs/calibration_data.json"

# DHT22 сензори
DHT_SENSOR_INSIDE = adafruit_dht.DHT22(board.D4)
DHT_SENSOR_OUTSIDE = adafruit_dht.DHT22(board.D17)

def save_calibration_data(data):
    """
    Записва калибрационните данни във файл.
    """
    try:
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("Calibration data saved successfully.")
    except Exception as e:
        log_error_to_file("CALIBRATION_SAVE_ERROR", f"Failed to save calibration data: {e}")

def load_calibration_data():
    """
    Зарежда калибрационните данни от файл.
    """
    try:
        with open(CALIBRATION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No valid calibration data found. Returning default values.")
        return {}

def calibrate_mq135():
    """
    Калибрира MQ-135 газовия сензор.
    """
    try:
        baseline = random.uniform(0, 0.5)  # Replace with actual calibration logic
        print(f"MQ-135 baseline set to {baseline}")
        return {"baseline": baseline}
    except Exception as e:
        log_error_to_file("MQ135_CALIBRATION_FAIL", str(e))
        return None

def calibrate_max4466():
    """
    Калибрира микрофонния сензор GY-MAX4466.
    """
    try:
        baseline = random.uniform(20, 40)  # Replace with actual calibration logic
        print(f"MAX4466 baseline set to {baseline}")
        return {"baseline": baseline}
    except Exception as e:
        log_error_to_file("MAX4466_CALIBRATION_FAIL", str(e))
        return None

def calibrate_hx711():
    """
    Калибрира HX711 сензора за тегло.
    """
    try:
        baseline = random.uniform(0, 10)  # Replace with actual calibration logic
        print(f"HX711 baseline set to {baseline}")
        return {"baseline": baseline}
    except Exception as e:
        log_error_to_file("HX711_CALIBRATION_FAIL", str(e))
        return None

def calibrate_bmp280():
    """
    Калибрира BMP280 сензора за налягане.
    """
    try:
        with SMBus(1) as bus:
            baseline = random.uniform(1000, 1020)  # Replace with actual calibration logic
            print(f"BMP280 baseline set to {baseline}")
            return {"baseline": baseline}
    except Exception as e:
        log_error_to_file("BMP280_CALIBRATION_FAIL", str(e))
        return None

def calibrate_dht22(sensor, sensor_name):
    """
    Калибрира DHT22 сензор.
    """
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        print(f"{sensor_name} calibrated: temperature={temperature}, humidity={humidity}")
        return {"temperature_baseline": temperature, "humidity_baseline": humidity}
    except RuntimeError as e:
        log_error_to_file(f"{sensor_name}_CALIBRATION_FAIL", str(e))
        return None

def calibrate_sensors():
    """
    Калибрира всички сензори и записва резултатите.
    """
    calibration_data = {}
    
    print("Starting sensor calibration...")
    calibration_data["mq135"] = calibrate_mq135()
    calibration_data["max4466"] = calibrate_max4466()
    calibration_data["hx711"] = calibrate_hx711()
    calibration_data["bmp280"] = calibrate_bmp280()
    calibration_data["dht_inside"] = calibrate_dht22(DHT_SENSOR_INSIDE, "DHT_INSIDE")
    calibration_data["dht_outside"] = calibrate_dht22(DHT_SENSOR_OUTSIDE, "DHT_OUTSIDE")
    
    save_calibration_data(calibration_data)
    print("Sensor calibration completed.")
