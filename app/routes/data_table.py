import json
import os
from flask import Blueprint, render_template, current_app, request, jsonify
import sqlite3

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
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'table_data.json')
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

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'data', 'table_data.db')
app.config['DATABASE'] = db_path

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Get all table data
@app.route('/api/table_data', methods=['GET'])
def get_table_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM table_data')
    rows = cursor.fetchall()
    return jsonify(rows)

# Add a new row
@app.route('/api/table_data', methods=['POST'])
def add_table_data():
    db = get_db()
    cursor = db.cursor()
    data = request.get_json()
    column1 = data.get('column1')
    column2 = data.get('column2')
    cursor.execute(
        'INSERT INTO table_data (column1, column2) VALUES (?, ?)',
        (column1, column2)
    )
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'column1': column1, 'column2': column2})

# Update a row
@app.route('/api/table_data/<int:id>', methods=['PUT'])
def update_table_data(id):
    db = get_db()
    cursor = db.cursor()
    data = request.get_json()
    column1 = data.get('column1')
    column2 = data.get('column2')
    cursor.execute(
        'UPDATE table_data SET column1 = ?, column2 = ? WHERE id = ?',
        (column1, column2, id)
    )
    db.commit()
    return jsonify({'id': id, 'column1': column1, 'column2': column2})

# Delete a row
@app.route('/api/table_data/<int:id>', methods=['DELETE'])
def delete_table_data(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM table_data WHERE id = ?', (id,))
    db.commit()
    return jsonify({'deleted': id})