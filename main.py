# main.py
import os
from app import create_app, socketio
from flask import render_template
from app.routes.data_table import bp as data_table_bp

app = create_app()
app.register_blueprint(data_table_bp)

@app.route('/datatable')
def datatable():
    return render_template('datatable.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
