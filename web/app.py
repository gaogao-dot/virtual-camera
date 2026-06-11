"""
Flask Web 应用
"""

from flask import Flask
from flask_cors import CORS
from config import WEB_CONFIG

def create_app(virtual_camera_app=None):
    app = Flask(__name__)
    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = WEB_CONFIG['max_content_length']
    app.config['VIRTUAL_CAMERA_APP'] = virtual_camera_app
    from .routes import create_routes
    create_routes(app)
    return app
