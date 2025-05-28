import json
import os
import sqlite3
from flask import Blueprint, render_template, current_app, request, jsonify, g

bp = Blueprint('datatable', __name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = os.path.join(current_app.root_path, 'data', 'table_data.db')
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@bp.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@bp.route("/datatable/")
@bp.route("/datatable")
def data_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM table_data')
    rows = cursor.fetchall()
    # Convert rows to list of dicts for Jinja
    table_data = [dict(row) for row in rows]

    help_text = (
        "Voltage at pot2 wiper (pin 17).<br>"
        "Brake_Pot_Percent CAN = 0x33D3:00, Node ID = 0x27"
    )

    return render_template("data_table.html",
                           table_data=table_data,
                           help_text=help_text)

# API: Get all table data
@bp.route('/api/table_data', methods=['GET'])
def get_table_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM table_data')
    rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows])

# API: Add a new row
@bp.route('/api/table_data', methods=['POST'])
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

# API: Update a row
@bp.route('/api/table_data/<int:id>', methods=['PUT'])
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

# API: Delete a row
@bp.route('/api/table_data/<int:id>', methods=['DELETE'])
def delete_table_data(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM table_data WHERE id = ?', (id,))
    db.commit()
    return jsonify({'deleted': id})

# Optional: Save multiple changes (if your frontend sends a batch)
@bp.route('/save_table_json', methods=['POST'])
def save_table_json():
    data = request.get_json()
    changes = data.get('changes', [])
    db = get_db()
    cursor = db.cursor()
    try:
        # Clear table and insert new data
        cursor.execute('DELETE FROM table_data')
        for row in changes:
            cursor.execute(
                'INSERT INTO table_data (column1, column2) VALUES (?, ?)',
                (row.get('column1'), row.get('column2'))
            )
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        print("Error saving to DB:", e)
        return jsonify({'success': False}), 500