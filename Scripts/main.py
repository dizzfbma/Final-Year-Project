import os
import time
import threading
import subprocess
import db
from watchers import CowrieLogHandler
from openwatcher import OpenCanaryLogHandler
from webapp import socketio, app  # Flask-SocketIO app
from watchdog.observers import Observer

# === CONFIG ===
COWRIE_JSON_PATH = "/home/spinn/final-year-project/cowrie/var/log/cowrie/cowrie.json"
OPENCANARY_LOG_PATH = "/var/tmp/opencanary.log"

# === WATCHERS ===
def start_watchers():
    """Start both Cowrie and OpenCanary log monitoring."""
    observer = Observer()

    # Cowrie log watcher
    if os.path.exists(COWRIE_JSON_PATH):
        cowrie = CowrieLogHandler(COWRIE_JSON_PATH)
        cowrie.start()
        observer.schedule(cowrie, path=os.path.dirname(COWRIE_JSON_PATH), recursive=False)
        print("[+] Watching Cowrie logs...")
    else:
        print(f"[!] Cowrie log not found: {COWRIE_JSON_PATH}")

    # OpenCanary log watcher
    if os.path.exists(OPENCANARY_LOG_PATH):
        opencanary = OpenCanaryLogHandler(OPENCANARY_LOG_PATH)
        opencanary.start()
        observer.schedule(opencanary, path=os.path.dirname(OPENCANARY_LOG_PATH), recursive=False)
        print("[+] Watching OpenCanary logs...")
    else:
        print(f"[!] OpenCanary log not found: {OPENCANARY_LOG_PATH}")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping observers...")
        observer.stop()
        observer.join()
        print("[+] Observers stopped.")

# === FLASK ===
def start_flask():
    """Run the Flask app with WebSockets enabled."""
    print("[+] Starting Flask server on http://0.0.0.0:5000 ...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)


# === MAIN ===
def main():
    """Start everything: DB, watchers, Flask."""
    db.init_db()

    # Start watchers in thread
    watcher_thread = threading.Thread(target=start_watchers, daemon=True)
    watcher_thread.start()

    # Start Flask (main thread)
    start_flask()


if __name__ == "__main__":
    main()
