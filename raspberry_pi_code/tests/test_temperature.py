from raspberry_pi_code.hardware_layer.sensors import read_dht22, DHT_SENSOR_INSIDE

def test_temperature():
    temperature, _ = read_dht22(DHT_SENSOR_INSIDE)
    if temperature is not None:
        print(f"Temperature (DHT22): {temperature} °C")
    else:
        print("Failed to read temperature from DHT22 sensor.")

if __name__ == "__main__":
    test_temperature()
