from flask import Blueprint, render_template, request, jsonify, send_file
from flask_socketio import emit
import csv, os, time
from datetime import datetime

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
    if request.headers.get("Authorization", "").split()[-1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([data.get("timestamp"), data.get("id"), data.get("data")])
    emit("can_message", data, broadcast=True)
    return jsonify({"status": "received"}), 200

@can_monitor_bp.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    if request.headers.get("Authorization", "").split()[-1] != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    emit("heartbeat", {"status": "online", "ts": time.time()}, broadcast=True)
    return jsonify({"status": "ok"}), 200

@can_monitor_bp.route("/logs/download")
def download_logs():
    return send_file(CSV_FILE, as_attachment=True)
