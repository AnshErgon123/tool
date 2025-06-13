# ERGON CAN Monitor Web Application

A full-stack, real-time CAN bus monitoring and configuration interface developed at **Ergon Labs**. This project enables seamless diagnostics, data streaming, and dynamic parameter updates for embedded vehicular systems using a modern browser-based frontend and backend integration with PEAK CAN hardware.

---

## Project Overview

The CAN Monitor Web App bridges physical CAN interfaces (via USB) and an intuitive web dashboard. Designed to support in-field vehicle diagnostics and parameter configuration, it offers:

- Real-time data feed from CAN hardware
- Secure, socket-based communication protocol
- Firebase-integrated parameter dashboard
- CSV logging and download functionality

---

## Technology Stack

| Layer        | Technologies Used                                       |
|-------------|----------------------------------------------------------|
| **Frontend** | React.js, Socket.IO Client, Firebase Firestore          |
| **Backend**  | Node.js, Express.js, Socket.IO Server                   |
| **Hardware** | Python (PCAN Integration), python-can, socketio-client |
| **Database** | Firebase Firestore (Cloud-hosted NoSQL)                |

---

## Key Features

- **Handshake & Acknowledgment Protocol**: Securely initiates communication with the CAN client and verifies connection via ACK.
- **Real-Time Monitoring**: Streams incoming CAN messages to the frontend via WebSockets.
- **Editable Parameter Table**: Integrates with Firebase to display and update per-vehicle CAN parameters.
- **Validation & Logging**: Supports field validation, change tracking, and auto-logging of edits.
- **CSV Export**: One-click download of live CAN message logs in CSV format.
- **Vehicle Filter**: View and edit parameters per vehicle context with selection dropdown.

---

## Project Structure

```plaintext
/ergon-can-monitor
│
├── server.js                # Express.js server & WebSocket event hub
├── client/
│   └── can_client.py        # Python-based CAN listener and dispatcher (PCAN)
│
├── frontend/
│   ├── firebase.js          # Firebase app and Firestore setup
│   ├── CanMonitor.js        # React component: Real-time CAN feed with filters
│   └── DataTable.js         # React component: Editable parameter dashboard
│
└── public/
    └── data_table.json      # Static backup of CAN parameters (optional)
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ergon-can-monitor.git
cd ergon-can-monitor
```

---

### 2. Install Dependencies

#### Backend (Node.js)

```bash
npm install
```

#### Python CAN Client

```bash
cd client
pip install -r requirements.txt
# Or install manually:
pip install python-can python-socketio python-dotenv requests
```

---

### 3. Firebase Configuration

Update the Firebase config in `frontend/firebase.js` with your project credentials:

```js
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  ...
};
```

Ensure your Firestore has:
- `vehicles` collection
- `canParameters` collection

---

### 4. Environment Setup for Python Client

Create a `.env` file in `/client`:

```dotenv
SERVER_URL=http://localhost:10000
SECRET_TOKEN=supersecret
```

---

### 5. Run the System

#### Start Backend Server

```bash
node server.js
```

#### Start CAN Client (Python)

Make sure PEAK CAN USB hardware is connected:

```bash
python can_client.py
```

#### Run Frontend

If integrated in a React app, run via:

```bash
npm start
```

Or serve the static build using a tool like `serve`.

---

| Method | Endpoint            | Description                               |
| ------ | ------------------- | ----------------------------------------- |
| POST   | `/api/handshake`    | Initiates handshake with CAN client       |
| POST   | `/api/request_data` | Requests data frame from CAN client       |
| POST   | `/api/send_data`    | Receives CAN data and emits via WebSocket |
| POST   | `/api/ack`          | ACK signal receiver and frontend notifier |
| GET    | `/api/data_table`   | Retrieves static JSON data table          |
| PUT    | `/api/data_table`   | Updates the static JSON data table        |
| GET    | `/logs/download`    | Downloads logged CAN data as CSV          |

---

## Security & Communication

- The CAN client registers via a secure token (`SECRET_TOKEN`).
- Handshake and data requests are socket-triggered and confirmed via ACK.
- All messages include timestamps and CAN IDs for traceability.

---

## Developer & Acknowledgments

**Developed by:**  
[Ansh Vivek Malhotra](https://github.com/anshvm) — *Final Year CSE Undergraduate, NITK Surathkal*

**Under the guidance of:**  
- **Jacob Phillip** – Lead Engineer, Ergon Labs  
- **Ashwin Ramanujam** – CEO, Ergon Mobility

---

## License

This project is proprietary and developed at Ergon Labs. Contact [Ergon Mobility](mailto:ansh.malhotra@ergon-labs.com) for usage permissions.

---
