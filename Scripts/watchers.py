from webapp import broadcast_new_event  # Import WebSocket function
from ml import run_anomaly_detection
import db
import json
import os
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

COWRIE_JSON_PATH = "/home/spinn/final-year-project/cowrie/var/log/cowrie/cowrie.json"

class CowrieLogHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.abspath(file_path)
        self._file = None
        self._file_position = 0

    def start(self):
        """Open the log file and move to the end so only new lines are read."""
        if not os.path.exists(self.file_path):
            print(f"[ERROR] File not found: {self.file_path}")
            return

        self._file = open(self.file_path, "r", encoding="utf-8")
        self._file.seek(0, 2)  # Move to end
        self._file_position = self._file.tell()
        print(f"[+] Watching {self.file_path} for changes...")

    def stop(self):
        """Close the file when stopping."""
        if self._file:
            self._file.close()
            print("[+] Log file closed.")

    def on_modified(self, event):
        """Triggered when the log file is modified."""
        if os.path.abspath(event.src_path) == self.file_path:
            self._read_new_lines()

    def _read_new_lines(self):
        """Read and process new lines added to the log file."""
        if not self._file:
            print("[WARNING] Log file is not open.")
            return

        self._file.seek(self._file_position)
        lines = self._file.readlines()
        self._file_position = self._file.tell()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                self._process_event(data)
            except json.JSONDecodeError:
                print(f"[ERROR] Failed to parse JSON: {line}")

    def _process_event(self, data):
        """Process login and command events."""
        eventid = data.get("eventid", "")
        timestamp = data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        src_ip = data.get("src_ip", "Unknown")
        username = data.get("username", "N/A")
        password = data.get("password", "N/A")
        input_cmd = data.get("input", "")

        is_anomaly = False
        if eventid in ["cowrie.login.failed", "cowrie.login.success"]:
            is_anomaly = run_anomaly_detection(src_ip, username, password, "")
            db.insert_event(timestamp, src_ip, username, password, "", is_anomaly)
            print(f"[LOG] [{timestamp}] {eventid}: {username} from {src_ip} - Anomaly: {is_anomaly}")

        elif eventid == "cowrie.command.input":
            is_anomaly = run_anomaly_detection(src_ip, "", "", input_cmd)
            db.insert_event(timestamp, src_ip, "", "", input_cmd, is_anomaly)
            print(f"[LOG] [{timestamp}] Command from {src_ip}: {input_cmd} - Anomaly: {is_anomaly}")

        # Send real-time update to frontend
        event_json = {
            "timestamp": timestamp,
            "src_ip": src_ip,
            "username": username,
            "password": password,
            "commands": input_cmd,
            "is_anomaly": is_anomaly
        }
        broadcast_new_event(event_json)

def monitor_cowrie():
    """Start monitoring Cowrie logs using watchdog."""
    if not os.path.exists(COWRIE_JSON_PATH):
        print(f"[ERROR] Cannot find {COWRIE_JSON_PATH}. Exiting...")
        return

    observer = Observer()
    handler = CowrieLogHandler(COWRIE_JSON_PATH)
    handler.start()

    observer.schedule(handler, path=os.path.dirname(COWRIE_JSON_PATH), recursive=False)
    observer.start()

    try:
        print("[+] Watchdog Observer Running...")
        while True:
            time.sleep(1)  # Reduce CPU usage
    except KeyboardInterrupt:
        print("\n[!] Stopping Watchdog Observer...")
        observer.stop()
        handler.stop()
        observer.join()
        print("[+] Observer stopped successfully.")

if __name__ == "__main__":
    monitor_cowrie()
