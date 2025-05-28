import json
from flask import Blueprint, render_template, current_app, request, jsonify
import can  # Add this import
import traceback

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

    # 1. Load current table data
    json_path = current_app.root_path + "/data/data_table.json"
    with open(json_path, "r") as f:
        table_data = json.load(f)

    # 2. Update project values in table_data
    for change in changes:
        for row in table_data:
            if row["name"] == change["name"]:
                value = change["updated_project_value"]
                # Add % or Hz if min/max has it
                if isinstance(row["min"], str) and row["min"].endswith("%"):
                    value = f"{value} %"
                elif isinstance(row["min"], str) and row["min"].endswith("Hz"):
                    value = f"{value} Hz"
                row["project"] = value

    # 3. Save updated data back to JSON
    with open(json_path, "w") as f:
        json.dump(table_data, f, indent=2)
    print("Updated JSON:", table_data)

    # 4. Read the updated JSON file again
    with open(json_path, "r") as f:
        updated_table_data = json.load(f)

    # 5. Send updated values from JSON to CAN bus
    try:
        bus = can.interface.Bus(channel='PCAN_USB', bustype='pcan')
        for row in updated_table_data:
            if row["name"] == "Brake_Pot_Percent":
                can_id = 0x33D3
                # Remove unit for sending
                value_str = str(row["project"]).split()[0]
                value = int(float(value_str))
                data = [value & 0xFF]
                msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
                bus.send(msg)
        bus.shutdown()
    except Exception as e:
        print("CAN bus send error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": True}), 200
