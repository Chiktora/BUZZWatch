from flask import Blueprint, jsonify
from raspberry_pi_code.errors import log_error_to_file

sensor_api = Blueprint('sensor_api', __name__)

@sensor_api.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        data = {"temperature": 25.5, "humidity": 45.2}
        return jsonify(data), 200
    except Exception as e:
        log_error_to_file("SENSOR_DATA_ERROR", str(e))
        return jsonify({"status": "error", "message": "Failed to retrieve sensor data."}), 500
