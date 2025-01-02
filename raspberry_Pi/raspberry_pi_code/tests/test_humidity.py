from raspberry_pi_code.hardware_layer.sensors import read_dht22, DHT_SENSOR_INSIDE

def test_humidity():
    _, humidity = read_dht22(DHT_SENSOR_INSIDE)
    if humidity is not None:
        print(f"Humidity (DHT22): {humidity} %")
    else:
        print("Failed to read humidity from DHT22 sensor.")

if __name__ == "__main__":
    test_humidity()
