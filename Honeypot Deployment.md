# Honeypot Project - Deployment Instructions

This guide explains how to start, stop, and run your honeypot environment, which includes:

- **Cowrie (SSH/Telnet honeypot)**
- **OpenCanary (Multiple protocol honeypot)**
- **Flask Web Dashboard (for real-time log visualization and anomaly detection)**

---

## Cowrie Honeypot

### ✅ Start Cowrie
```bash
cd ~/final-year-project/cowrie
source cowrie-env/bin/activate
./bin/cowrie start
```

### ❌ Stop Cowrie
```bash
./bin/cowrie stop
```

---

## OpenCanary

> Make sure `twistd` is available in your `PATH`:
```bash
export PATH="$HOME/.local/share/pipx/venvs/opencanary/bin:$PATH"
```

### ✅ Start OpenCanary
```bash
~/.local/bin/opencanaryd --start --no-daemon --config=/home/spinn/.opencanary.conf
```

### ❌ Stop OpenCanary
Find the process ID (PID):
```bash
ps aux | grep opencanary
```
Kill it:
```bash
sudo kill <PID>
```
Or more easily:
```bash
sudo pkill -f opencanary
```

---

## Flask Web Dashboard

### ✅ Start Flask Server
This runs the Flask dashboard, Cowrie log watcher, OpenCanary log watcher, and a simulated FTP attack generator:
```bash
cd ~/final-year-project/Scripts
source ../cowrie/cowrie-env/bin/activate
python3 main.py
```

### 📍 Access the Interface
Visit: [http://localhost:5000](http://localhost:5000)

### ❌ Stop Flask Server
Press `CTRL+C` in the terminal running the server.

---

## Summary

| Task                 | Command                                                                 |
|----------------------|-------------------------------------------------------------------------|
| ✅ Start Cowrie        | `./bin/cowrie start`                                                    |
| ❌ Stop Cowrie         | `./bin/cowrie stop`                                                     |
| ✅ Start OpenCanary    | `~/.local/bin/opencanaryd --start --no-daemon --config=/home/spinn/.opencanary.conf` |
| ❌ Stop OpenCanary     | `sudo pkill -f opencanary`                                              |
| ✅ Start Flask Server  | `python3 main.py`                                                       |
| ❌ Stop Flask Server   | CTRL+C                                                                  |

---

## Troubleshooting

- Flask Web UI shows no data? Check:
  - Cowrie and OpenCanary are running
  - Logs are being generated at:
    - `cowrie/var/log/cowrie/cowrie.json`
    - `/var/tmp/opencanary.log`
  - Your database `cowrie_events.db` is located in `database/` and is not locked

- Flask server won't quit with CTRL+C?
  - Make sure it's running in the foreground
  - If stuck, find the process with:
    ```bash
    lsof -i :5000
    kill -9 <PID>
    ```

---

Logs can be manually inspected at:

- `cowrie/var/log/cowrie/cowrie.json`
- `/var/tmp/opencanary.log`
- Combined (if applicable): `/var/tmp/honeypot_combined.log`

---

Happy Testing!
