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

class B92Protocol:
    def __init__(self, n_bits=100, qber=0.0, eve_present=False, eve_interception_rate=0.0):
        self.n_bits = n_bits
        self.qber = qber
        self.eve_present = eve_present
        self.eve_interception_rate = eve_interception_rate
        self.channel = QuantumChannel(qber=qber)

    def run(self):
        # 1. Alice prepares qubits
        # Alice uses |0> for bit 0 and |+> for bit 1
        alice_bits = np.random.randint(0, 2, self.n_bits)
        qubits = []
        for bit in alice_bits:
            qubits.append(QuantumState.zero() if bit == 0 else QuantumState.plus())

        # 2. Transmission
        received_qubits = []
        eve_info = {"interceptions": 0}
        for q in qubits:
            if self.eve_present and np.random.random() < self.eve_interception_rate:
                # Eve measures in random basis (Z or X)
                eve_basis = np.random.choice(['Z', 'X'])
                measure(q, basis=eve_basis)
                eve_info["interceptions"] += 1
            received_qubits.append(self.channel.transmit(q))

        # 3. Bob measures
        # Bob measures in basis orthogonal to Alice's states: 
        # If he wants to detect |0>, he measures in X basis (looking for |-> result)
        # If he wants to detect |+>, he measures in Z basis (looking for |1> result)
        bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
        bob_results = []
        for q, basis in zip(received_qubits, bob_bases):
            bob_results.append(measure(q, basis=basis))

        # 4. Sifting
        # Bob only keeps results where he got a '1' (which indicates he detected the state)
        # If basis was X and result was 1 -> Alice sent |0> (bit 0)
        # If basis was Z and result was 1 -> Alice sent |+> (bit 1)
        sifted_indices = []
        alice_sifted = []
        bob_sifted = []
        
        for i in range(self.n_bits):
            if bob_results[i] == 1:
                sifted_indices.append(i)
                alice_sifted.append(alice_bits[i])
                # Bob's bit inference:
                if bob_bases[i] == 'X':
                    bob_sifted.append(0)
                else:
                    bob_sifted.append(1)

        if len(sifted_indices) > 0:
            errors = np.sum(np.array(alice_sifted) != np.array(bob_sifted))
            calculated_qber = errors / len(sifted_indices)
        else:
            calculated_qber = 0

        return {
            "alice_bits": alice_bits.tolist(),
            "bob_results": bob_results,
            "sifted_indices": sifted_indices,
            "alice_sifted": alice_sifted,
            "bob_sifted": bob_sifted,
            "qber": calculated_qber,
            "eve_info": eve_info
        }

class E91Protocol:
    def __init__(self, n_bits=100, qber=0.0, eve_present=False, eve_interception_rate=0.0):
        self.n_bits = n_bits
        self.qber = qber
        self.eve_present = eve_present
        self.eve_interception_rate = eve_interception_rate

    def run(self):
        # 1. Source creates entangled pairs
        # We simulate the correlation directly
        alice_bases = np.random.choice(['Z', 'X', 'W'], self.n_bits) # W is a third basis for CHSH
        bob_bases = np.random.choice(['Z', 'X', 'W'], self.n_bits)
        
        alice_bits = []
        bob_bits = []
        
        for i in range(self.n_bits):
            # Generate entangled result
            res = np.random.randint(0, 2)
            a_res = res
            b_res = res # Perfect correlation in same basis
            
            # Apply noise
            if np.random.random() < self.qber:
                b_res = 1 - b_res
                
            # Eve attack (Interception)
            if self.eve_present and np.random.random() < self.eve_interception_rate:
                # Eve breaks entanglement by measuring
                b_res = np.random.randint(0, 2)
            
            # Correlation based on basis difference
            if alice_bases[i] != bob_bases[i]:
                # In different bases, results are partially correlated
                # For simplicity in simulation, we use random results for different bases
                b_res = np.random.randint(0, 2)
                
            alice_bits.append(a_res)
            bob_bits.append(b_res)

        # 2. Sifting
        sifted_indices = [i for i in range(self.n_bits) if alice_bases[i] == bob_bases[i]]
        alice_sifted = [alice_bits[i] for i in sifted_indices]
        bob_sifted = [bob_bits[i] for i in sifted_indices]

        if len(sifted_indices) > 0:
            errors = np.sum(np.array(alice_sifted) != np.array(bob_sifted))
            calculated_qber = errors / len(sifted_indices)
        else:
            calculated_qber = 0

        return {
            "alice_bits": alice_bits,
            "alice_bases": alice_bases.tolist(),
            "bob_bits": bob_bits,
            "bob_bases": bob_bases.tolist(),
            "sifted_indices": sifted_indices,
            "alice_sifted": alice_sifted,
            "bob_sifted": bob_sifted,
            "qber": calculated_qber,
            "eve_info": {"interceptions": int(self.eve_interception_rate * self.n_bits) if self.eve_present else 0}
        }
