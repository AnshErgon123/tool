from flask import Flask
from flask_socketio import SocketIO
from .routes.can_monitor import can_monitor_bp

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__, static_folder="static")
    app.register_blueprint(can_monitor_bp)
    return app
