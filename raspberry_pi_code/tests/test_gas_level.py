from raspberry_pi_code.hardware_layer.sensors import read_mq135

def test_gas_level():
    gas_level = read_mq135()
    if gas_level is not None:
        print(f"Gas Level (MQ-135): {gas_level}")
    else:
        print("Failed to read gas level from MQ-135 sensor.")

if __name__ == "__main__":
    test_gas_level()