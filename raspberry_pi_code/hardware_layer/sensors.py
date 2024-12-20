from Adafruit_DHT import DHT22, read_retry
from hx711 import HX711
from smbus2 import SMBus
from bmp280 import BMP280

TEMP_HUM_SENSOR_PIN = 4
LOAD_CELL_DT = 5
LOAD_CELL_SCK = 6
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

hx = HX711(LOAD_CELL_DT, LOAD_CELL_SCK)
hx.set_reading_format("MSB", "MSB")
hx.tare()

def read_temp_hum():
    humidity, temperature = read_retry(DHT22, TEMP_HUM_SENSOR_PIN)
    return {
        "temperature": round(temperature, 2) if temperature is not None else None,
        "humidity": round(humidity, 2) if humidity is not None else None,
    }

def read_weight():
    weight = hx.get_weight(5)
    hx.power_down()
    hx.power_up()
    return round(weight, 2)

def read_atmospheric_data():
    pressure = bmp280.get_pressure()
    temperature = bmp280.get_temperature()
    return {
        "pressure": round(pressure, 2),
        "temperature": round(temperature, 2),
    }
