from flask import Blueprint, request, jsonify

sensor_data = Blueprint('sensor_data', __name__)

@sensor_data.route('/sensor_data', methods=['POST'])
def upload_sensor_data():
    """
    Получава данни от сензори и ги обработва.
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    print(f"Received data: {data}")
    return jsonify({"status": "success", "message": "Data processed successfully"}), 200
