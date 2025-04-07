from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO
import time
import db
from ml import run_anomaly_detection

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

socketio = SocketIO(app)  # Enables WebSockets


@app.route("/")
def index():
    """Renders the main dashboard page with real-time attack logs."""
    rows = db.get_recent_events(50)  # Fetch latest 50 events
    events = format_events(rows)
    return render_template("index.html", events=events)


@app.route("/simulate")
def simulate():
    """Renders the simulated honeypot interaction UI."""
    return render_template("simulated.html")


@app.route("/api/events")
def api_events():
    """Returns attack logs as JSON for external integrations."""
    rows = db.get_recent_events(100)  # Fetch latest 100 events
    return jsonify(format_events(rows))


@app.route("/api/simulated-attack", methods=["POST"])
def simulated_attack():
    """
    Handles simulated attack submissions from the simulated UI.
    It logs the event in the database with source 'simulated' and emits it via SocketIO.
    """
    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")
    command = data.get("command", "")
    src_ip = request.headers.get("X-Forwarded-For", request.remote_addr)  # <-- updated here
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    is_anomaly = run_anomaly_detection(src_ip, username, password, command)
    db.insert_event(timestamp, src_ip, username, password, command, is_anomaly, source="simulated")

    event = {
        "timestamp": timestamp,
        "src_ip": src_ip,
        "username": username,
        "password": password,
        "commands": command,
        "is_anomaly": is_anomaly,
        "source": "simulated"
    }
    socketio.emit("new_event", event)

    return jsonify({"message": f"Simulated attack logged (Anomaly: {'Yes' if is_anomaly else 'No'})"})


def format_events(rows):
    """
    Format database query results into structured JSON.
    Expected columns: timestamp, src_ip, username, password, commands, is_anomaly, source
    """
    return [{
        "timestamp": r[0] if r[0] else "N/A",
        "src_ip": r[1] if r[1] else "Unknown",
        "username": r[2] if r[2] else "N/A",
        "password": r[3] if r[3] else "N/A",
        "commands": r[4] if r[4] else "N/A",
        "is_anomaly": bool(r[5]) if r[5] is not None else False,
        "source": r[6] if len(r) > 6 and r[6] else "cowrie"
    } for r in rows]


def broadcast_new_event(event):
    """Emit new events to WebSocket clients."""
    socketio.emit("new_event", event)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)

