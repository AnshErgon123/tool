import os
import time
import can
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Load from .env or use default values
# Make sure your .env file in the client directory has these:
# SERVER_URL=https://your-render-app-name.onrender.com
# SECRET_TOKEN=supersecret
SERVER_URL = os.getenv("SERVER_URL", "https://tool-t8tp.onrender.com") # Update with your actual Render URL
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "supersecret")

print(f"SERVER_URL: {SERVER_URL}")
print(f"SECRET_TOKEN: {SECRET_TOKEN}")

HEADERS = {
    "Authorization": f"Bearer {SECRET_TOKEN}",
    "Content-Type": "application/json"
}

# Configure your CAN interface here.
# 'pcan' and 'PCAN_USBBUS1' are specific to Peak CAN devices.
# Adjust these based on your CAN hardware (e.g., 'socketcan' for Linux, 'kvaser', etc.)
can_interface = 'pcan'
can_channel = 'PCAN_USBBUS1'

RETRY_DELAY = 5         # seconds to wait on failure before retrying POST requests
HEARTBEAT_INTERVAL = 10 # seconds between heartbeat pings to the server

def send_heartbeat():
    try:
        print("Sending heartbeat...")
        # Note: The heartbeat URL now correctly points to /api/heartbeat
        res = requests.post(f"{SERVER_URL}/api/heartbeat", headers=HEADERS, timeout=5) # Added timeout
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
    bus = None # Initialize bus to None

    # Loop to attempt CAN bus connection until successful
    while bus is None:
        try:
            bus = can.interface.Bus(
                channel=can_channel,
                interface=can_interface,
                receive_own_messages=True # ✅ Allow receiving messages sent by USB-CAN tool
            )
            print(f"🚗 Successfully connected to CAN channel: {can_channel}")
        except can.CanError as e:
            print(f"❌ CAN interface error: {e}. Retrying in {RETRY_DELAY} seconds...")
            bus = None # Reset bus to None to re-enter loop
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"❌ Unexpected error during CAN connection: {e}. Retrying in {RETRY_DELAY} seconds...")
            bus = None # Reset bus to None to re-enter loop
            time.sleep(RETRY_DELAY)


    while True:
        current_time = time.time()
        if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
            send_heartbeat()
            last_heartbeat = current_time

        msg = None
        try:
            msg = bus.recv(0.1) # Timeout of 100ms
        except can.CanError as e:
            print(f"❌ Error receiving CAN message: {e}. Attempting to re-establish bus connection.")
            bus.shutdown() # Shut down the problematic bus
            bus = None
            # Re-attempt connection in the outer while loop
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
            continue # Continue to the next iteration of the main loop to process messages


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
                res = requests.post(f"{SERVER_URL}/api/send_data", json=payload, headers=HEADERS, timeout=5) # Added timeout
                if res.status_code == 200:
                    print(f"✅ Sent: {payload}")
                else:
                    print(f"⚠ Failed to send data: {res.status_code} {res.text}")
                    time.sleep(RETRY_DELAY) # Wait before retrying if server returns an error
            except requests.exceptions.Timeout:
                print(f"❌ Network error: Request timed out for {SERVER_URL}/api/send_data")
                time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Network error: Connection failed to {SERVER_URL}/api/send_data - {e}")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"❌ Unexpected error sending data: {e}")
                time.sleep(RETRY_DELAY)

        # Small delay to prevent busy-waiting, even if no message is received
        time.sleep(0.01) # Shorter sleep here as bus.recv already has a timeout

if __name__ == "__main__":
    main()