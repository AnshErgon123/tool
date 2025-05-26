from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'

    from app.routes.can_monitor import can_monitor_bp
    app.register_blueprint(can_monitor_bp)

    socketio.init_app(app)
    return app
