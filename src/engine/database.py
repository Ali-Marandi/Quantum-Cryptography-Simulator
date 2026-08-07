import sqlite3
import os

class QCryptoDB:
    """Manages simulation history in a local SQLite database."""
    def __init__(self, db_path="qcrypto_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                protocol TEXT,
                qber REAL,
                key_length INTEGER,
                security_score INTEGER,
                eve_detected BOOLEAN
            )
        ''')
        conn.commit()
        conn.close()

    def save_simulation(self, protocol, qber, key_length, sec_score, eve_detected):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (protocol, qber, key_length, security_score, eve_detected)
            VALUES (?, ?, ?, ?, ?)
        ''', (protocol, qber, key_length, sec_score, eve_detected))
        conn.commit()
        conn.close()

    def get_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT 20')
        rows = cursor.fetchall()
        conn.close()
        return rows
