import json
from flask import Blueprint, render_template, current_app, request, jsonify

bp = Blueprint('datatable', __name__)
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

@bp.route("/datatable/apply", methods=["POST"])
def apply_changes():
    data = request.get_json()
    changes = data.get("changes", [])

    # Load current table data
    json_path = current_app.root_path + "/data/data_table.json"
    with open(json_path, "r") as f:
        table_data = json.load(f)

    # Update project values in table_data
    for change in changes:
        for row in table_data:
            if row["name"] == change["name"]:
                row["project"] = change["updated_project_value"]

    # Save updated data back to JSON
    with open(json_path, "w") as f:
        json.dump(table_data, f, indent=2)

    # TODO: Send updated values to CAN bus here if needed

    return jsonify({"success": True})
