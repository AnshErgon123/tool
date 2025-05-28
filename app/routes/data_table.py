from flask import request, jsonify
import can  # Assuming you use python-can or similar

@bp.route("/apply_changes", methods=["POST"])
def apply_changes():
    data = request.get_json()
    changes = data.get("changes", [])

    try:
        for item in changes:
            name = item["name"]
            value = item["updated_project_value"]

            # Convert value to the format your CAN bus expects
            can_id = 0x33D3  # example CAN ID
            can_data = [int(value)] + [0x00] * 7  # pad with 0s to 8 bytes

            # Send to CAN bus
            msg = can.Message(arbitration_id=can_id, data=can_data, is_extended_id=False)
            bus = can.interface.Bus(channel='can0', bustype='socketcan')  # adjust if needed
            bus.send(msg)

        return jsonify({"message": "Changes sent to CAN successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
