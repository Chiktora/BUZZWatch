from raspberry_pi_code.hardware_layer.sensors import read_max4466

def test_sound_level():
    sound_level = read_max4466()
    if sound_level is not None:
        print(f"Sound Level (GY-MAX4466): {sound_level}")
    else:
        print("Failed to read sound level from GY-MAX4466 sensor.")

if __name__ == "__main__":
    test_sound_level()
