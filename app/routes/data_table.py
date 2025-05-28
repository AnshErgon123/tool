import json
from flask import Blueprint, render_template, current_app, request, jsonify

bp = Blueprint('datatable', __name__)
@bp.route("/datatable/")
@bp.route("/datatable")
def data_table():
    # Construct path relative to app root
    json_path = current_app.root_path + "/data/data_table.json"
    with open(json_path, "r") as f:
        table_data = json.load(f)

    help_text = (
        "Voltage at pot2 wiper (pin 17).<br>"
        "Brake_Pot_Percent CAN = 0x33D3:00, Node ID = 0x27"
    )

    return render_template("data_table.html",
                           table_data=table_data,
                           help_text=help_text)

@bp.route("/datatable/update", methods=["POST"])
def update_data_table():
    json_path = current_app.root_path + "/data/data_table.json"
    data = request.get_json()
    table_data = data.get("table_data")
    if table_data is None:
        return jsonify({"message": "No data provided"}), 400

    with open(json_path, "w") as f:
        json.dump(table_data, f, indent=2)

    return jsonify({"message": "Table updated successfully"})