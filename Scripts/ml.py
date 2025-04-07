import numpy as np
import time
import joblib
import hashlib
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

# Constants
WINDOW_SIZE = 500
MODEL_TRAIN_THRESHOLD = 50

# Models
ISOLATION_MODEL = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
SVM_MODEL = OneClassSVM(kernel="rbf", gamma="auto")
MODEL_DATA = []

# IP State Tracking
ATTACK_HISTORY = defaultdict(int)
FEATURE_CACHE = {}
LAST_SEEN = {}


def run_anomaly_detection(src_ip, username, password, commands):
    features = event_to_features(src_ip, username, password, commands)
    MODEL_DATA.append(features)

    if len(MODEL_DATA) > WINDOW_SIZE:
        MODEL_DATA[:] = MODEL_DATA[-WINDOW_SIZE:]

    if len(MODEL_DATA) > MODEL_TRAIN_THRESHOLD:
        X = np.array(MODEL_DATA)
        ISOLATION_MODEL.fit(X)
        SVM_MODEL.fit(X)

        X_test = np.array([features])
        pred_iso = ISOLATION_MODEL.predict(X_test)[0]
        pred_svm = SVM_MODEL.predict(X_test)[0]

        score = 0
        if pred_iso == -1:
            score += 1
        if pred_svm == -1:
            score += 1
        if features[-1] < 0.5:
            score += 1
        if np.log(ATTACK_HISTORY[src_ip] + 1) > 4:  # only if VERY frequent
            score += 1

        # Debugging output to see what's going on
        print(f"[ML] IP: {src_ip}, ISO: {pred_iso}, SVM: {pred_svm}, TimeDiff: {features[-1]:.2f}, FreqLog: {np.log(ATTACK_HISTORY[src_ip] + 1):.2f}, FinalScore: {score}")

        return score >= 3  # More strict threshold

    # Not enough data to make a solid decision yet
    return False


def event_to_features(src_ip, username, password, commands):
    # Last octet
    last_octet = int(src_ip.split('.')[-1]) if '.' in src_ip else 0

    # Shannon entropy
    entropy = ip_entropy(src_ip)

    # Hashes
    user_hash = int(hashlib.md5(username.encode()).hexdigest(), 16) % 10000
    pass_hash = int(hashlib.md5(password.encode()).hexdigest(), 16) % 10000

    # Commands
    cmd_len = len(commands)
    cmd_diversity = len(set(commands)) if commands else 0

    # Frequency
    ATTACK_HISTORY[src_ip] += 1
    attack_freq = np.log(ATTACK_HISTORY[src_ip] + 1)

    # Time-based
    time_diff = time_since_last(src_ip)

    return [
        float(last_octet),
        float(entropy),
        float(user_hash),
        float(pass_hash),
        float(cmd_len),
        float(cmd_diversity),
        float(attack_freq),
        float(time_diff)
    ]


def ip_entropy(ip):
    if ip in FEATURE_CACHE:
        return FEATURE_CACHE[ip]

    freqs = defaultdict(int)
    for char in ip:
        freqs[char] += 1
    entropy = -sum((f / len(ip)) * np.log2(f / len(ip)) for f in freqs.values())

    FEATURE_CACHE[ip] = entropy
    return entropy


def time_since_last(ip):
    now = time.time()
    diff = now - LAST_SEEN.get(ip, now)
    LAST_SEEN[ip] = now
    return diff
