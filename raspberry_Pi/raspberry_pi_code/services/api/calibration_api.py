from flask import Blueprint, request, jsonify
import json
from raspberry_pi_code.errors import log_error_to_file

calibration_api = Blueprint('calibration_api', __name__)

CALIBRATION_FILE = "/home/pi/BUZZWatch/raspberry_pi_code/configs/calibration_data.json"

def load_calibration_data():
    try:
        with open(CALIBRATION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_error_to_file("LOAD_CALIBRATION_ERROR", str(e))
        return {}

def save_calibration_data(data):
    try:
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        log_error_to_file("SAVE_CALIBRATION_ERROR", str(e))
        return False

@calibration_api.route('/calibration', methods=['GET', 'POST'])
def calibration():
    if request.method == 'GET':
        return jsonify(load_calibration_data()), 200
    if request.method == 'POST':
        new_data = request.json
        calibration_data = load_calibration_data()
        calibration_data.update(new_data)
        if save_calibration_data(calibration_data):
            return jsonify({"status": "success", "message": "Calibration data updated."}), 200
        return jsonify({"status": "error", "message": "Failed to save calibration data."}), 500
