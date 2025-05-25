# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_TOKEN")

    from app.routes.can_monitor import can_monitor_bp
    app.register_blueprint(can_monitor_bp)

    socketio.init_app(app)
    return app
