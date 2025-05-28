import json
import os
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

@bp.route('/save_table_json', methods=['POST'])
def save_table_json():
    data = request.get_json()
    changes = data.get('changes', [])
    
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'table_data.json')
    json_path = os.path.abspath(json_path)

    print(f"[DEBUG] Saving to: {json_path}")
    print(f"[DEBUG] Received data: {json.dumps(changes, indent=2)}")

    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(changes, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({'success': False}), 500
