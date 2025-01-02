from flask import Blueprint, jsonify
from raspberry_pi_code.utils.system_utils import get_system_state
from raspberry_pi_code.errors import log_error_to_file

system_state_api = Blueprint('system_state_api', __name__)

@system_state_api.route('/system_state', methods=['GET'])
def system_state():
    try:
        state = get_system_state()
        return jsonify(state), 200
    except Exception as e:
        log_error_to_file("SYSTEM_STATE_ERROR", str(e))
        return jsonify({"status": "error", "message": "Failed to retrieve system state."}), 500
