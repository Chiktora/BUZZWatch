from flask import Blueprint
from .sensor_data import sensor_data

def create_routes(app):
    app.register_blueprint(sensor_data)
