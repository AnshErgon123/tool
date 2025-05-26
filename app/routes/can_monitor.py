import sys
import os
from flask import Blueprint, render_template, request, jsonify, send_file
import csv
from datetime import datetime
from app import socketio  # ✅ import the socketio instance

can_monitor_bp = Blueprint("can_monitor", __name__)
CSV_FILE = "can_log.csv"  # This will be created in the root directory where the app runs
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

# Ensure the CSV file exists with headers if it's new
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "id", "data"])

initialize_csv() # Call this when the blueprint is registered or app starts

@can_monitor_bp.route("/")
def home():
    return render_template("home.html")

@can_monitor_bp.route("/can-monitor")
def can_monitor_home():
    return render_template("can_monitor.html")

@can_monitor_bp.route("/api/send_data", methods=["POST"])
def receive_data():
    try:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split()[-1] if auth_header else ""

        if token != SECRET_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}

        # --- WARNING: Local CSV logging is NOT persistent on platforms like Render.com ---
        # Data written here will be lost when the container restarts.
        # For production, consider using a database (PostgreSQL, MongoDB)
        # or a cloud storage service (AWS S3, Google Cloud Storage) for persistent logging.
        try:
            with open(CSV_FILE, "a", newline="") as f:
                csv.writer(f).writerow([
                    data.get("timestamp", datetime.utcnow().isoformat()),
                    data.get("id", "N/A"),
                    data.get("data", "N/A")
                ])
        except IOError as e:
            print(f"⚠️ Warning: Could not write to CSV file: {e}")
            # Optionally, you could log this to a persistent log service
            # or handle it differently if CSV writing is critical.

        # Emit data to connected WebSocket clients
        socketio.emit("can_message", data, broadcast=True)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("🔥 Error in /api/send_data:", e)
        return jsonify({"error": "Server error"}), 500

@can_monitor_bp.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    try:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split()[-1] if auth_header else ""

        if token != SECRET_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401

        # Optionally, you can log the heartbeat or update a "last seen" timestamp for the client
        print("❤️ Heartbeat received from client.")
        return jsonify({"status": "Heartbeat received"}), 200

    except Exception as e:
        print("🔥 Error in /api/heartbeat:", e)
        return jsonify({"error": "Server error"}), 500

@can_monitor_bp.route("/logs/download")
def download_logs():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No logs found"}), 404
    # Note: On Render, this will only download logs from the current instance's uptime.
    # It won't contain historical data if the container has restarted.
    return send_file(CSV_FILE, as_attachment=True, mimetype='text/csv')

# Don't forget to register this blueprint in your main app.py
# Example in main app.py:
# from can_monitor import can_monitor_bp
# app.register_blueprint(can_monitor_bp)