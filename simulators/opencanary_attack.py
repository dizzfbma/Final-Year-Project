import socket
import requests
import random
import time

OPENCANARY_IP = "127.0.0.1"  # Change to your OpenCanary IP if remote

# Common attack simulations
def simulate_ftp():
    try:
        s = socket.socket()
        s.connect((OPENCANARY_IP, 21))
        s.sendall(b"USER anonymous\r\n")
        s.sendall(b"PASS anonymous\r\n")
        s.close()
        print("[+] Simulated FTP login")
    except Exception as e:
        print("[!] FTP error:", e)

def simulate_telnet():
    try:
        s = socket.socket()
        s.connect((OPENCANARY_IP, 23))
        s.sendall(b"admin\r\n")
        s.sendall(b"password\r\n")
        s.close()
        print("[+] Simulated Telnet login")
    except Exception as e:
        print("[!] Telnet error:", e)

def simulate_http():
    try:
        res = requests.get(f"http://{OPENCANARY_IP}", timeout=2)
        print("[+] Simulated HTTP GET:", res.status_code)
    except Exception as e:
        print("[!] HTTP error:", e)

def simulate_mysql():
    try:
        s = socket.socket()
        s.connect((OPENCANARY_IP, 3306))
        s.sendall(b"\x00\x00\x00\x01")  # Just random MySQL binary junk
        s.close()
        print("[+] Simulated MySQL connection")
    except Exception as e:
        print("[!] MySQL error:", e)

def simulate_smb():
    try:
        s = socket.socket()
        s.connect((OPENCANARY_IP, 445))
        s.sendall(b"\x00\x00\x00\x90")  # Random SMB junk
        s.close()
        print("[+] Simulated SMB probe")
    except Exception as e:
        print("[!] SMB error:", e)

# Dispatcher
attack_functions = [simulate_ftp, simulate_telnet, simulate_http, simulate_mysql, simulate_smb]

# Run multiple simulations
for i in range(30):  # Simulate 30 attacks
    random.choice(attack_functions)()
    time.sleep(0.5)
