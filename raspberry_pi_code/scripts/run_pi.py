from data_collection_layer.data_collector import collect_data
from data_collection_layer.upload_manager import upload_data

def main_loop():
    while True:
        temp_hum, weight, atmospheric, image_path = collect_data()
        data = {
            "temperature": temp_hum["temperature"],
            "humidity": temp_hum["humidity"],
            "weight": weight,
            "pressure": atmospheric["pressure"],
            "atmospheric_temperature": atmospheric["temperature"],
            "image_path": image_path,
        }
        upload_data(data)
