from raspberry_pi_code.hardware_layer.sensors import read_hx711

def test_weight():
    weight = read_hx711()
    if weight is not None:
        print(f"Weight (HX711): {weight}")
    else:
        print("Failed to read weight from HX711 sensor.")

if __name__ == "__main__":
    test_weight()
