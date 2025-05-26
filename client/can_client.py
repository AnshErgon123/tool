# (Your can_client.py content - no changes needed here)
import os
import time
import can
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv() # Loads from .env in the same directory by default

SERVER_URL = os.getenv("SERVER_URL", "https://tool-t8tp.onrender.com")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "supersecret")

print(f"SERVER_URL: {SERVER_URL}")
print(f"SECRET_TOKEN: {SECRET_TOKEN}")

HEADERS = {
    "Authorization": f"Bearer {SECRET_TOKEN}",
    "Content-Type": "application/json"
}

can_interface = 'pcan'
can_channel = 'PCAN_USBBUS1'

RETRY_DELAY = 5
HEARTBEAT_INTERVAL = 10
REQUEST_TIMEOUT = 5

def send_heartbeat():
    try:
        print("Sending heartbeat...")
        res = requests.post(f"{SERVER_URL}/api/heartbeat", headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            print("❤️ Heartbeat sent successfully.")
        else:
            print(f"⚠ Heartbeat failed: {res.status_code} - {res.text}")
    except requests.exceptions.Timeout:
        print("❌ Heartbeat error: Request timed out.")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Heartbeat error: Connection failed - {e}")
    except Exception as e:
        print("❌ Heartbeat error:", e)

def main():
    last_heartbeat = 0
    bus = None

    while bus is None:
        try:
            bus = can.interface.Bus(
                channel=can_channel,
                interface=can_interface,
                receive_own_messages=True
            )
            print(f"🚗 Successfully connected to CAN channel: {can_channel}")
        except can.CanError as e:
            print(f"❌ CAN interface error: {e}. Retrying in {RETRY_DELAY} seconds...")
            bus = None
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"❌ Unexpected error during CAN connection: {e}. Retrying in {RETRY_DELAY} seconds...")
            bus = None
            time.sleep(RETRY_DELAY)

    while True:
        current_time = time.time()
        if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
            send_heartbeat()
            last_heartbeat = current_time

        msg = None
        try:
            msg = bus.recv(0.1)
        except can.CanError as e:
            print(f"❌ Error receiving CAN message: {e}. Attempting to re-establish bus connection.")
            if bus:
                bus.shutdown()
            bus = None
            while bus is None:
                try:
                    bus = can.interface.Bus(
                        channel=can_channel,
                        interface=can_interface,
                        receive_own_messages=True
                    )
                    print(f"🚗 Reconnected to CAN channel: {can_channel}")
                except can.CanError as reconnect_e:
                    print(f"❌ Reconnection failed: {reconnect_e}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                except Exception as reconnect_e:
                    print(f"❌ Unexpected error during reconnection: {reconnect_e}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
            continue

        if msg:
            timestamp_str = datetime.fromtimestamp(msg.timestamp).isoformat()
            can_id_str = f"{msg.arbitration_id:03X}"
            data_str = ' '.join(f"{b:02X}" for b in msg.data)

            payload = {
                "timestamp": timestamp_str,
                "id": can_id_str,
                "data": data_str
            }

            try:
                res = requests.post(f"{SERVER_URL}/api/send_data", json=payload, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if res.status_code == 200:
                    print(f"✅ Sent: {payload}")
                else:
                    print(f"⚠ Failed to send data: {res.status_code} {res.text}")
                    time.sleep(RETRY_DELAY)
            except requests.exceptions.Timeout:
                print(f"❌ Network error: Request timed out for {SERVER_URL}/api/send_data")
                time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Network error: Connection failed to {SERVER_URL}/api/send_data - {e}")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"❌ Unexpected error sending data: {e}")
                time.sleep(RETRY_DELAY)

        time.sleep(0.01)

if __name__ == "__main__":
    main()