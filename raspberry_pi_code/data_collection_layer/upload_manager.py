import requests

CLOUD_URL = "https://example-cloud-endpoint.com/upload"

def upload_data(data):
    response = requests.post(CLOUD_URL, json=data, timeout=10)
    return response.status_code
