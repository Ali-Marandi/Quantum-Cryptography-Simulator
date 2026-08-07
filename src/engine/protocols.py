import numpy as np
from .quantum_engine import QuantumState, QuantumChannel, measure, PhotonSource, Detector, FreeSpaceChannel

class BB84Protocol:
    def __init__(self, n_bits=100, qber=0.0, distance=0.0, eve_present=False, eve_interception_rate=0.0, 
                 source_type="SinglePhoton", detector_efficiency=1.0, channel_type="Fiber", **kwargs):
        self.n_bits = n_bits
        self.qber = qber
        self.distance = distance
        self.eve_present = eve_present
        self.eve_interception_rate = eve_interception_rate
        self.source = PhotonSource(source_type=source_type)
        self.detector = Detector(efficiency=detector_efficiency)
        
        if channel_type == "Satellite":
            self.channel = FreeSpaceChannel(altitude=kwargs.get('altitude', 500), 
                                           weather=kwargs.get('weather', 'Clear'), 
                                           turbulence=kwargs.get('turbulence', 'Low'))
        else:
            self.channel = QuantumChannel(None, None, qber=qber, distance=distance)

    def run(self, attack_type=None):
        # 1. Alice prepares qubits
        alice_bits = np.random.randint(0, 2, self.n_bits)
        alice_bases = np.random.choice(['Z', 'X'], self.n_bits)
        
        transmitted_photon_packets = []
        for bit, basis in zip(alice_bits, alice_bases):
            state = QuantumState.zero() if bit == 0 else QuantumState.one()
            if basis == 'X':
                state = QuantumState.plus() if bit == 0 else QuantumState.minus()
            
            photons = self.source.emit(state)
            transmitted_photon_packets.append(photons)

        # 2. Transmission (with possible Eve attacks)
        received_qubits = []
        eve_info = {"interceptions": 0, "pns_leaks": 0}
        
        if attack_type == "DetectorBlinding":
            self.detector.is_blinded = True

        for photons in transmitted_photon_packets:
            if not photons:
                received_qubits.append(None)
                continue
                
            q = photons[0]
            
            if self.eve_present:
                if attack_type == "PNS" and len(photons) > 1:
                    eve_q = photons[0]
                    q = photons[1]
                    eve_info["pns_leaks"] += 1
                elif np.random.random() < self.eve_interception_rate:
                    measure(q, basis=np.random.choice(['Z', 'X']))
                    eve_info["interceptions"] += 1
            
            received_qubits.append(self.channel.transmit(q))

        # 3. Bob measures
        bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
        bob_bits = []
        for q, basis in zip(received_qubits, bob_bases):
            if q is not None and np.random.random() < self.detector.efficiency:
                bob_bits.append(measure(q, basis=basis))
            else:
                bob_bits.append(None)

        # 4. Sifting
        sifted_indices = []
        alice_sifted = []
        bob_sifted = []
        for i in range(self.n_bits):
            if alice_bases[i] == bob_bases[i] and bob_bits[i] is not None:
                sifted_indices.append(i)
                alice_sifted.append(alice_bits[i])
                bob_sifted.append(bob_bits[i])

        if len(sifted_indices) > 0:
            errors = np.sum(np.array(alice_sifted) != np.array(bob_sifted))
            calculated_qber = errors / len(sifted_indices)
        else:
            calculated_qber = 0

        return {
            "alice_bits": alice_bits.tolist(),
            "alice_bases": alice_bases.tolist(),
            "bob_bits": bob_bits,
            "bob_bases": bob_bases.tolist(),
            "sifted_indices": sifted_indices,
            "alice_sifted": alice_sifted,
            "bob_sifted": bob_sifted,
            "qber": calculated_qber,
            "eve_info": eve_info
        }

class B92Protocol:
    def __init__(self, n_bits=100, qber=0.0, distance=0.0, eve_present=False, eve_interception_rate=0.0):
        self.n_bits, self.qber, self.distance, self.eve_present, self.eve_interception_rate = n_bits, qber, distance, eve_present, eve_interception_rate
        self.channel = QuantumChannel(None, None, qber=qber, distance=distance)

    def run(self):
        alice_bits = np.random.randint(0, 2, self.n_bits)
        qubits = [QuantumState.zero() if b == 0 else QuantumState.plus() for b in alice_bits]
        received_qubits = []
        eve_info = {"interceptions": 0}
        for q in qubits:
            if self.eve_present and np.random.random() < self.eve_interception_rate:
                measure(q, basis=np.random.choice(['Z', 'X']))
                eve_info["interceptions"] += 1
            received_qubits.append(self.channel.transmit(q))
        bob_bases = np.random.choice(['Z', 'X'], self.n_bits)
        bob_results = [measure(q, basis=b) for q, b in zip(received_qubits, bob_bases)]
        sifted_indices = [i for i in range(self.n_bits) if bob_results[i] == 1]
        alice_sifted = [alice_bits[i] for i in sifted_indices]
        bob_sifted = [0 if bob_bases[i] == 'X' else 1 for i in sifted_indices]
        qber = np.sum(np.array(alice_sifted) != np.array(bob_sifted)) / len(sifted_indices) if sifted_indices else 0
        return {"alice_bits": alice_bits.tolist(), "sifted_indices": sifted_indices, "alice_sifted": alice_sifted, "bob_sifted": bob_sifted, "qber": qber, "eve_info": eve_info}

class E91Protocol:
    def __init__(self, n_bits=100, qber=0.0, distance=0.0, eve_present=False, eve_interception_rate=0.0):
        self.n_bits, self.qber, self.distance, self.eve_present, self.eve_interception_rate = n_bits, qber, distance, eve_present, eve_interception_rate

    def run(self):
        alice_bases = np.random.choice(['Z', 'X', 'W'], self.n_bits)
        bob_bases = np.random.choice(['Z', 'X', 'W'], self.n_bits)
        alice_bits, bob_bits = [], []
        for i in range(self.n_bits):
            res = np.random.randint(0, 2)
            a_res, b_res = res, res
            if np.random.random() < self.qber: b_res = 1 - b_res
            if self.eve_present and np.random.random() < self.eve_interception_rate: b_res = np.random.randint(0, 2)
            if alice_bases[i] != bob_bases[i]: b_res = np.random.randint(0, 2)
            alice_bits.append(a_res); bob_bits.append(b_res)
        sifted_indices = [i for i in range(self.n_bits) if alice_bases[i] == bob_bases[i]]
        alice_sifted = [alice_bits[i] for i in sifted_indices]
        bob_sifted = [bob_bits[i] for i in sifted_indices]
        qber = np.sum(np.array(alice_sifted) != np.array(bob_sifted)) / len(sifted_indices) if sifted_indices else 0
        return {"alice_bits": alice_bits, "alice_sifted": alice_sifted, "bob_sifted": bob_sifted, "qber": qber, "eve_info": {"interceptions": int(self.eve_interception_rate * self.n_bits) if self.eve_present else 0}}

class NetworkQKD:
    def __init__(self, network, start_node, end_node, protocol_type="BB84", n_bits=100):
        self.network, self.start_node, self.end_node, self.protocol_type, self.n_bits = network, start_node, end_node, protocol_type, n_bits
        
    def run(self):
        path = self.network.get_path(self.start_node, self.end_node)
        if not path:
            return {"status": "No secure path found in the 3D quantum network."}
            
        # Simulate multi-hop key distribution
        total_qber = 0
        all_alice_sifted = []
        all_bob_sifted = []
        
        for ch in path:
            # Each hop is a separate QKD session
            hop_protocol = BB84Protocol(n_bits=self.n_bits, distance=ch.distance, qber=ch.qber)
            hop_results = hop_protocol.run()
            total_qber += hop_results['qber']
            # In a real network, keys are XORed or routed. Here we simulate the final key length.
            if not all_alice_sifted:
                all_alice_sifted = hop_results['alice_sifted']
                all_bob_sifted = hop_results['bob_sifted']
            else:
                # Key length might decrease due to routing overhead/security
                min_len = min(len(all_alice_sifted), len(hop_results['alice_sifted']))
                all_alice_sifted = all_alice_sifted[:min_len]
                all_bob_sifted = all_bob_sifted[:min_len]

        avg_qber = total_qber / len(path)
        return {
            "hops": len(path),
            "alice_sifted": all_alice_sifted,
            "bob_sifted": all_bob_sifted,
            "qber": avg_qber,
            "status": f"Secure Multi-hop Routing Successful ({len(path)} hops)"
        }
