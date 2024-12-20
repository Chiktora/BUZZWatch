from hardware_layer.sensors import read_temp_hum, read_weight, read_atmospheric_data
from hardware_layer.camera import capture_image

def collect_data():
    temp_hum = read_temp_hum()
    weight = read_weight()
    atmospheric = read_atmospheric_data()
    image_path = capture_image()
    return temp_hum, weight, atmospheric, image_path
