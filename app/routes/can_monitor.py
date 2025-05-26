import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from flask import Blueprint, render_template, request, jsonify, send_file
import csv
from datetime import datetime
from app import socketio  # ✅ import the socketio instance

can_monitor_bp = Blueprint("can_monitor", __name__)
CSV_FILE = "can_log.csv"
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

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

        # Save to CSV
        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                data.get("timestamp", datetime.utcnow().isoformat()),
                data.get("id", "N/A"),
                data.get("data", "N/A")
            ])

        # Emit data to connected WebSocket clients
        socketio.emit("can_message", data, broadcast=True)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("🔥 Error in /api/send_data:", e)
        return jsonify({"error": "Server error"}), 500

@can_monitor_bp.route("/logs/download")
def download_logs():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No logs found"}), 404
    return send_file(CSV_FILE, as_attachment=True)
