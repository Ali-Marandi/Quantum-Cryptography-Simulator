import numpy as np
from .quantum_engine import QuantumState, QuantumChannel, measure

class BB84Protocol:
    def __init__(self, n_bits=100, qber=0.0, eve_present=False, eve_interception_rate=0.0):
        self.n_bits = n_bits
        self.qber = qber
        self.eve_present = eve_present
        self.eve_interception_rate = eve_interception_rate
        self.channel = QuantumChannel(qber=qber)

    def run(self):
        # 1. Alice prepares qubits
        alice_bits = np.random.randint(0, 2, self.n_bits)
        alice_bases = np.random.choice(['Z', 'X'], self.n_bits)
        
        qubits = []
        for bit, basis in zip(alice_bits, alice_bases):
            if basis == 'Z':
                qubits.append(QuantumState.zero() if bit == 0 else QuantumState.one())
            else:
                qubits.append(QuantumState.plus() if bit == 0 else QuantumState.minus())

        # 2. Transmission (with possible Eve interception)
        received_qubits = []
        eve_info = {"interceptions": 0, "bits": [], "bases": []}
        
        for q in qubits:
            if self.eve_present and np.random.random() < self.eve_interception_rate:
                # Eve intercepts and resends
                eve_basis = np.random.choice(['Z', 'X'])
                eve_bit = measure(q, basis=eve_basis)
                eve_info["interceptions"] += 1
                eve_info["bits"].append(eve_bit)
                eve_info["bases"].append(eve_basis)
                
                # Resend new qubit in the basis Eve measured
                if eve_basis == 'Z':
                    q = QuantumState.zero() if eve_bit == 0 else QuantumState.one()
                else:
                    q = QuantumState.plus() if eve_bit == 0 else QuantumState.minus()
            
            # Channel noise
            received_qubits.append(self.channel.transmit(q))

        # 3. Bob measures
        bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
        bob_bits = []
        for q, basis in zip(received_qubits, bob_bases):
            bob_bits.append(measure(q, basis=basis))

        # 4. Sifting
        sifted_indices = [i for i in range(self.n_bits) if alice_bases[i] == bob_bases[i]]
        alice_sifted = alice_bits[sifted_indices]
        bob_sifted = np.array(bob_bits)[sifted_indices]

        # 5. Error Rate Calculation
        if len(sifted_indices) > 0:
            errors = np.sum(alice_sifted != bob_sifted)
            calculated_qber = errors / len(sifted_indices)
        else:
            calculated_qber = 0

        return {
            "alice_bits": alice_bits.tolist(),
            "alice_bases": alice_bases.tolist(),
            "bob_bits": bob_bits,
            "bob_bases": bob_bases.tolist(),
            "sifted_indices": sifted_indices,
            "alice_sifted": alice_sifted.tolist(),
            "bob_sifted": bob_sifted.tolist(),
            "qber": calculated_qber,
            "eve_info": eve_info
        }
