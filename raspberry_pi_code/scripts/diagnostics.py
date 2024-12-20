import time
from hardware_layer.sensors import read_temp_hum, read_weight, read_atmospheric_data
from hardware_layer.camera import capture_image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Diagnostics functions

def diagnose_temp_hum():
    """Diagnoses the temperature and humidity sensor."""
    logging.info("Diagnosing DHT22 sensor...")
    temp_hum = read_temp_hum()
    if temp_hum["temperature"] is not None and temp_hum["humidity"] is not None:
        logging.info(f"DHT22 OK: Temperature={temp_hum['temperature']}°C, Humidity={temp_hum['humidity']}%")
        return True
    else:
        logging.error("DHT22 Error: Unable to read temperature or humidity.")
        return False

def diagnose_weight():
    """Diagnoses the weight sensor (HX711)."""
    logging.info("Diagnosing HX711 sensor...")
    try:
        weight = read_weight()
        if weight is not None:
            logging.info(f"HX711 OK: Weight={weight}g")
            return True
        else:
            logging.error("HX711 Error: Unable to read weight.")
            return False
    except (RuntimeError, IOError) as e:
        logging.error(f"HX711 Error: {e}")
        return False

def diagnose_atmospheric():
    """Diagnoses the atmospheric pressure and temperature sensor (BMP280)."""
    logging.info("Diagnosing BMP280 sensor...")
    atmospheric = read_atmospheric_data()
    if atmospheric["pressure"] is not None and atmospheric["temperature"] is not None:
        logging.info(f"BMP280 OK: Pressure={atmospheric['pressure']} hPa, Temperature={atmospheric['temperature']}°C")
        return True
    else:
        logging.error("BMP280 Error: Unable to read pressure or temperature.")
        return False

def diagnose_camera():
    """Diagnoses the PiCamera."""
    logging.info("Diagnosing PiCamera...")
    try:
        image_path = capture_image()
        if image_path:
            logging.info(f"PiCamera OK: Image saved at {image_path}")
            return True
        else:
            logging.error("PiCamera Error: Unable to capture image.")
            return False
    except (IOError, RuntimeError) as e:
        logging.error(f"PiCamera Error: {e}")
        return False

def run_diagnostics():
    """Runs diagnostics for all sensors."""
    logging.info("Starting diagnostics...")
    dht22_status = diagnose_temp_hum()
    hx711_status = diagnose_weight()
    bmp280_status = diagnose_atmospheric()
    picamera_status = diagnose_camera()

    results = {
        "DHT22": dht22_status,
        "HX711": hx711_status,
        "BMP280": bmp280_status,
        "PiCamera": picamera_status
    }

    logging.info("Diagnostics complete.")
    for sensor, status in results.items():
        logging.info(f"{sensor}: {'OK' if status else 'Error'}")
    return results

# Calibration functions

def calibrate_hx711():
    """Calibrates the HX711 weight sensor."""
    logging.info("Calibrating HX711 sensor...")
    try:
        from hx711 import HX711
        hx = HX711(LOAD_CELL_DT, LOAD_CELL_SCK)
        hx.set_reading_format("MSB", "MSB")
        logging.info("Setting tare to 0...")
        hx.tare()
        logging.info("HX711 calibration complete. Tare set to 0.")
        return True
    except (RuntimeError, IOError) as e:
        logging.error(f"HX711 Calibration Error: {e}")
        return False

# Entry point for diagnostics and calibration
if __name__ == "__main__":
    logging.info("Running sensor diagnostics...")
    diagnostic_results = run_diagnostics()

    logging.info("Running sensor calibration...")
    calibrate_hx711()

    logging.info("All diagnostics and calibration processes completed.")
