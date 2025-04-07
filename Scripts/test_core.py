import unittest
import os
import sqlite3
from ml import event_to_features, ip_entropy, time_since_last, ATTACK_HISTORY
import db

class TestAnomalyFeatures(unittest.TestCase):

    def test_ip_entropy(self):
        ip = "192.168.1.1"
        entropy = ip_entropy(ip)
        self.assertTrue(entropy > 0)
        self.assertIsInstance(entropy, float)

    def test_event_to_features_format(self):
        features = event_to_features("192.168.1.10", "admin", "1234", "ls -la")
        self.assertEqual(len(features), 8)
        self.assertIsInstance(features[0], float)

    def test_time_since_last_monotonic(self):
        ip = "10.0.0.5"
        t1 = time_since_last(ip)
        t2 = time_since_last(ip)
        self.assertTrue(t2 < 2.0)  # should be fast

    def test_attack_history_increment(self):
        ip = "8.8.8.8"
        ATTACK_HISTORY[ip] = 5
        event_to_features(ip, "user", "pass", "ls")
        self.assertTrue(ATTACK_HISTORY[ip] >= 6)


class TestDatabaseFunctions(unittest.TestCase):

    def setUp(self):
        self.test_db_path = "test_events.db"
        db.DB_PATH = self.test_db_path
        db.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_insert_and_fetch_event(self):
        db.insert_event("2025-04-03 12:00:00", "1.2.3.4", "admin", "1234", "ls", True, "simulated")
        events = db.get_recent_events(1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1], "1.2.3.4")  # IP

    def test_auto_trim(self):
        for i in range(1100):
            db.insert_event(f"2025-04-03 12:{i//60}:{i%60}", f"10.0.0.{i%255}", "user", "pass", "ls", False, "cowrie")
        db.clear_old_events(max_records=1000)
        with sqlite3.connect(self.test_db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM events")
            total = cur.fetchone()[0]
            self.assertLessEqual(total, 1000)

if __name__ == '__main__':
    unittest.main()
