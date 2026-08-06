from .protocols import BB84Protocol, B92Protocol, E91Protocol
from .quantum_engine import QuantumNetwork

class QCryptoSDK:
    """Professional SDK for integrating the Quantum Cryptography Simulator."""
    def __init__(self):
        self.network = QuantumNetwork()
        self.network.add_node("Alice")
        self.network.add_node("Bob")

    def run_bb84(self, n_bits=100, qber=0.01, distance=10.0):
        """Runs BB84 protocol and returns results."""
        protocol = BB84Protocol(n_bits=n_bits, qber=qber, distance=distance)
        return protocol.run()

    def run_b92(self, n_bits=100, qber=0.01, distance=10.0):
        """Runs B92 protocol and returns results."""
        protocol = B92Protocol(n_bits=n_bits, qber=qber, distance=distance)
        return protocol.run()

    def generate_etsi_report(self, results):
        """Generates a report compliant with ETSI GS QKD 014 standards (Simulated)."""
        report = {
            "version": "1.0",
            "standard": "ETSI GS QKD 014",
            "session_id": "QC-SIM-SESSION-001",
            "qber": results.get('qber', 0),
            "key_length": len(results.get('alice_sifted', [])),
            "status": "SECURE" if results.get('qber', 1) < 0.11 else "COMPROMISED"
        }
        return report
