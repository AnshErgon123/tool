import json
import os
from flask import Blueprint, render_template, current_app, request, jsonify, Flask

app = Flask(__name__)

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
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'data_table.json')
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        # Write the changes to the JSON file
        with open(json_path, 'w') as f:
            json.dump(changes, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        print("Error saving JSON:", e)
        return jsonify({'success': False}), 500

@app.route('/update_table', methods=['POST'])
def update_table():
    data = request.json
    # Save to your JSON file (replace 'your_data.json' with your actual file)
    with open('your_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'status': 'success'})