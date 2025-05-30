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
    from app.routes.data_table import bp as data_table_bp
    app.register_blueprint(data_table_bp)

    socketio.init_app(app)

    @app.route("/")
    def index():
        return "Welcome to the CAN Monitor!"

    return app
