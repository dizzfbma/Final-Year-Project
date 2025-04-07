import json
import os
from watchdog.events import FileSystemEventHandler
from ml import run_anomaly_detection
import db
from watchdog.observers import Observer
import time

class OpenCanaryLogHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self._file = None
        self._file_position = 0

    def start(self):
        if not os.path.exists(self.file_path):
            print(f"[!] OpenCanary log not found: {self.file_path}")
            return
        self._file = open(self.file_path, "r")
        self._file.seek(0, 2)
        self._file_position = self._file.tell()

    def on_modified(self, event):
        if event.src_path == self.file_path:
            self._read_new_lines()

    def _read_new_lines(self):
        self._file.seek(self._file_position)
        lines = self._file.readlines()
        self._file_position = self._file.tell()

        for line in lines:
            try:
                data = json.loads(line)
                self._process(data)
            except json.JSONDecodeError:
                pass

    def _process(self, data):
        timestamp = data.get("local_time", "")
        src_ip = data.get("src_host", "")
        protocol = data.get("logdata", {}).get("logdata", "OpenCanary Event")
        is_anomaly = run_anomaly_detection(src_ip, "", "", protocol)

        db.insert_event(timestamp, src_ip, "", "", protocol, is_anomaly, source="opencanary")

        print(f"[+] OpenCanary Event | {timestamp} | IP: {src_ip} | Protocol: {protocol} | Anomaly: {is_anomaly}")

if __name__ == "__main__":
    log_path = "/var/tmp/opencanary.log"
    handler = OpenCanaryLogHandler(log_path)
    handler.start()

    observer = Observer()
    observer.schedule(handler, path=os.path.dirname(log_path), recursive=False)
    observer.start()

    print("[*] Watching OpenCanary logs...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
