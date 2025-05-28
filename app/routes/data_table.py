import os
import json
from flask import Blueprint, render_template, request, jsonify, current_app

bp = Blueprint('datatable', __name__, url_prefix='/datatable')

@bp.route("/", methods=["GET"])
def data_table():
    json_path = os.path.join(current_app.root_path, "data", "data_table.json")
    with open(json_path, "r") as f:
        table_data = json.load(f)

    help_text = (
        "Voltage at pot2 wiper (pin 17).<br>"
        "Brake_Pot_Percent CAN = 0x33D3:00, Node ID = 0x27"
    )

    return render_template("data_table.html", table_data=table_data, help_text=help_text)

@bp.route("/update", methods=["POST"])
def update_table():
    json_path = os.path.join(current_app.root_path, "data", "data_table.json")

    try:
        updates = request.get_json()
        if not isinstance(updates, list):
            raise ValueError("Invalid data format")

        with open(json_path, "r") as f:
            table_data = json.load(f)

        for update in updates:
            for row in table_data:
                if row["name"] == update["name"]:
                    row["project"] = update["project"]
                    break

        with open(json_path, "w") as f:
            json.dump(table_data, f, indent=2)

        return jsonify(success=True)

    except Exception as e:
        current_app.logger.exception("Error updating JSON")
        return jsonify(success=False, error=str(e)), 400
