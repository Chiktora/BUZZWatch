import json

def save_to_local(data, file_path="local_data.json"):
    with open(file_path, "a") as file:
        json.dump(data, file)
        file.write("\\n")
