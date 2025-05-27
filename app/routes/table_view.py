from flask import Blueprint, render_template

bp = Blueprint('data_table', __name__)

@bp.route("/data-table")
def data_table():
    table_data = [
        {"name": "Brake Input", "device": "", "project": "", "min": "", "max": ""},
        {"name": "Mapped Brake", "device": "", "project": "", "min": "", "max": ""},
        {"name": "Brake Command", "device": "", "project": "", "min": "", "max": ""},
        {"name": "Brake Pedal Enable", "device": "➕", "project": "Off", "min": "Off", "max": "On"},
        {"name": "Brake Min Input", "device": "➖", "project": "15 %", "min": "0 %", "max": "100 %"},
        {"name": "Brake Max Input", "device": "➖", "project": "85 %", "min": "0 %", "max": "100 %"},
        {"name": "Brake Map Shape", "device": "➖", "project": "50 %", "min": "0 %", "max": "100 %"},
        {"name": "Brake Offset", "device": "➖", "project": "0 %", "min": "0 %", "max": "100 %"},
        {"name": "Brake Filter", "device": "➖", "project": "10.0 Hz", "min": "0.5 Hz", "max": "125.0 Hz"},
        {"name": "VCL Brake Enable", "device": "➕", "project": "Off", "min": "Off", "max": "On"},
    ]

    help_text = "Voltage at pot2 wiper (pin 17).<br>Brake_Pot_Percent CAN = 0x33D3:00, Node ID = 0x27"

    return render_template("data_table.html", table_data=table_data, help_text=help_text)
