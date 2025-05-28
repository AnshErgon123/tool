import json
from flask import Blueprint, render_template, current_app

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