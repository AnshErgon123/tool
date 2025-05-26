import os
from flask import Blueprint, render_template, request, jsonify, send_file
import csv
from datetime import datetime
from app import socketio  # ✅ import the socketio instance from your main app.py

can_monitor_bp = Blueprint("can_monitor", __name__)

# --- WARNING: Local CSV logging is NOT persistent on platforms like Render.com ---
# Data written here will be lost when the container restarts or scales.
# For production, consider using a persistent database (PostgreSQL, MongoDB)
# or a cloud storage service (AWS S3, Google Cloud Storage) for reliable logging.
CSV_FILE = "can_log.csv"
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret") # Server-side secret token

# Ensure the CSV file exists with headers if it's new
# This function will still run, but writing inside receive_data will be skipped.
def initialize_csv():
    # Only create if it doesn't exist to avoid overwriting on restart
    if not os.path.exists(CSV_FILE):
        print(f"Creating new CSV file: {CSV_FILE}")
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "id", "data"])
    else:
        print(f"CSV file already exists: {CSV_FILE}")

initialize_csv()


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
            print(f"Unauthorized access attempt to /api/send_data: Token mismatch")
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        # Ensure 'id' and 'data' are present and handle cases where they might be missing
        can_id = data.get("id", "N/A")
        can_data = data.get("data", "N/A")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        # ====================================================================
        # >>> TEMPORARILY COMMENTING OUT CSV WRITING TO AVOID 500 ERROR <<<
        # This allows Socket.IO emission to work.
        # ====================================================================
        # try:
        #     with open(CSV_FILE, "a", newline="") as f:
        #         csv.writer(f).writerow([timestamp, can_id, can_data])
        # except IOError as e:
        #     print(f"⚠️ Warning: Could not write to CSV file '{CSV_FILE}': {e}")
        #     # In a real application, you might log this error to a persistent logging service
        #     # or use a fallback storage mechanism.
        # ====================================================================

        # Emit data to connected WebSocket clients via SocketIO
        # This is how your web frontend (can_monitor.html) receives real-time updates.
        socketio.emit("can_message", data, broadcast=True)
        print(f"Received and emitted: {data}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"🔥 Error in /api/send_data: {e}", exc_info=True) # exc_info for full traceback
        return jsonify({"error": "Server error", "details": str(e)}), 500

@can_monitor_bp.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    try:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split()[-1] if auth_header else ""

        if token != SECRET_TOKEN:
            print(f"Unauthorized access attempt to /api/heartbeat: Token mismatch")
            return jsonify({"error": "Unauthorized"}), 401

        # Optionally, you can log the heartbeat or update a "last seen" timestamp for the client
        print("❤️ Heartbeat received from client.")
        return jsonify({"status": "Heartbeat received"}), 200

    except Exception as e:
        print(f"🔥 Error in /api/heartbeat: {e}", exc_info=True)
        return jsonify({"error": "Server error", "details": str(e)}), 500

@can_monitor_bp.route("/logs/download")
def download_logs():
    # If CSV writing is commented out, this endpoint will always return "No logs found"
    # or an empty CSV, as no data is being written persistently.
    if not os.path.exists(CSV_FILE):
        print(f"Download request for non-existent file: {CSV_FILE}")
        return jsonify({"error": "No logs found"}), 404

    try:
        print(f"Serving log file: {CSV_FILE}")
        return send_file(CSV_FILE, as_attachment=True, mimetype='text/csv', download_name="can_log.csv")
    except Exception as e:
        print(f"🔥 Error serving download: {e}", exc_info=True)
        return jsonify({"error": "Error downloading file", "details": str(e)}), 500