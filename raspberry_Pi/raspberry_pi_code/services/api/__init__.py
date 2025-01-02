from flask import Flask
from raspberry_pi_code.services.api.calibration_api import calibration_api
from raspberry_pi_code.services.api.sensor_data_api import sensor_api
from raspberry_pi_code.services.api.system_state_api import system_state_api
from raspberry_pi_code.services.api.config_api import config_api

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(calibration_api)
app.register_blueprint(sensor_api)
app.register_blueprint(system_state_api)
app.register_blueprint(config_api)
