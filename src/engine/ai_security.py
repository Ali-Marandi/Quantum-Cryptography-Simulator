import numpy as np
from sklearn.ensemble import IsolationForest

class AISecurity:
    """AI-powered security analysis for quantum key distribution."""
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        # Synthetic training data: [QBER, Key Rate, Error Pattern Variance]
        # Normal patterns (low QBER, stable rate)
        normal_data = np.random.normal(loc=[0.02, 0.5, 0.01], scale=[0.01, 0.05, 0.005], size=(100, 3))
        self.train(normal_data)

    def train(self, data):
        """Trains the anomaly detector on normal operation data."""
        self.model.fit(data)
        self.is_trained = True

    def detect_eavesdropping(self, qber, key_rate, variance):
        """Detects if current parameters indicate an anomaly (eavesdropping)."""
        if not self.is_trained:
            return False
        
        sample = np.array([[qber, key_rate, variance]])
        prediction = self.model.predict(sample)
        # -1 means anomaly, 1 means normal
        return prediction[0] == -1

    def optimize_parameters(self, distance, target_qber=0.05):
        """Suggests optimal mean photon number (mu) for WCP sources."""
        # Simplified optimization logic
        optimal_mu = max(0.01, 0.1 * np.exp(-distance / 50))
        return round(optimal_mu, 3)
