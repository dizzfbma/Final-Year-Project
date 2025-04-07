import os
import json
import time
import threading

COWRIE_LOG = "/home/spinn/final-year-project/cowrie/var/log/cowrie/cowrie.json"
OPENCANARY_LOG = "/var/tmp/opencanary.log"
COMBINED_LOG = "/var/tmp/honeypot_combined.log"


def tail_file(file_path, prefix, out_file):
    """Tails a log file and writes new entries to the combined log."""
    if not os.path.exists(file_path):
        print(f"[ERROR] {prefix} log file not found: {file_path}")
        return

    try:
        with open(file_path, "r") as f:
            f.seek(0, 2)  # Move to end of file

            while True:
                line = f.readline()
                if line:
                    log_entry = f"[{prefix}] {line.strip()}"
                    print(log_entry)  # Print to console for monitoring

                    with open(out_file, "a") as out:
                        out.write(log_entry + "\n")
                        out.flush()
                else:
                    time.sleep(0.5)  # Prevents high CPU usage
    except Exception as e:
        print(f"[ERROR] Issue with {prefix} log: {e}")


def combine_logs():
    """Starts tailing both Cowrie & OpenCanary logs in separate threads."""
    print("[+] Combining Cowrie & OpenCanary logs into:", COMBINED_LOG)

    cowrie_thread = threading.Thread(target=tail_file, args=(COWRIE_LOG, "COWRIE", COMBINED_LOG), daemon=True)
    opencanary_thread = threading.Thread(target=tail_file, args=(OPENCANARY_LOG, "OPENCANARY", COMBINED_LOG),
                                         daemon=True)

    cowrie_thread.start()
    opencanary_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[!] Stopping log collection...")
        cowrie_thread.join()
        opencanary_thread.join()
        print("[+] Log collection stopped.")


if __name__ == "__main__":
    combine_logs()
