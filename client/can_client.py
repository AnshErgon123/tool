import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "https://tool-t8tp.onrender.com")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "supersecret")

HEADERS = {
    "Authorization": f"Bearer {SECRET_TOKEN}",
    "Content-Type": "application/json"
}

def manual_send():
    while True:
        user_input = input("Enter CAN data (format: ID DATA, e.g. 123 11 22 33): ")
        try:
            parts = user_input.strip().split()
            if len(parts) < 2:
                print("Invalid input. Usage: ID DATA1 DATA2 ...")
                continue
            can_id_str = parts[0]
            data_str = ' '.join(parts[1:])
            timestamp_str = datetime.now().isoformat()
            payload = {
                "timestamp": timestamp_str,
                "id": can_id_str,
                "data": data_str
            }
            res = requests.post(f"{SERVER_URL}/api/send_data", json=payload, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                print(f"✅ Sent: {payload}")
            else:
                print(f"⚠ Failed to send data: {res.status_code} {res.text}")
        except Exception as e:
            print("Error sending manual data:", e)

if __name__ == "__main__":
    manual_send()