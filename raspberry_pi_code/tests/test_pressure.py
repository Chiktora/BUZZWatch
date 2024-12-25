from raspberry_pi_code.hardware_layer.sensors import read_bmp280

def test_pressure():
    pressure = read_bmp280()
    if pressure is not None:
        print(f"Pressure: {pressure} hPa")
    else:
        print("Failed to read pressure.")

if __name__ == "__main__":
    test_pressure()
