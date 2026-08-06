import numpy as np

class QuantumState:
    """Represents a single qubit state."""
    def __init__(self, state_vector):
        self.state = np.array(state_vector, dtype=complex)
        self.normalize()

    def normalize(self):
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state = self.state / norm

    @staticmethod
    def zero():
        return QuantumState([1, 0])

    @staticmethod
    def one():
        return QuantumState([0, 1])

    @staticmethod
    def plus():
        return QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])

    @staticmethod
    def minus():
        return QuantumState([1/np.sqrt(2), -1/np.sqrt(2)])

    @staticmethod
    def bell_state():
        """Returns a Bell state |phi+> = 1/sqrt(2) * (|00> + |11>).
        Note: For simplicity in our single-qubit engine, we'll return a pair of states
        that are correlated when measured in the same basis.
        """
        return None 

    def get_bloch_coordinates(self):
        """Returns (x, y, z) coordinates for Bloch sphere visualization."""
        a = self.state[0]
        b = self.state[1]
        x = 2 * np.real(np.conj(a) * b)
        y = 2 * np.imag(np.conj(a) * b)
        z = np.abs(a)**2 - np.abs(b)**2
        return x, y, z

class QuantumChannel:
    """Simulates a quantum channel with noise and distance modeling."""
    def __init__(self, qber=0.0, distance=0.0, attenuation_coeff=0.2):
        """
        distance: distance in km
        attenuation_coeff: loss in dB/km (default 0.2 for fiber)
        """
        self.distance = distance
        self.attenuation_coeff = attenuation_coeff
        
        # Calculate additional QBER due to distance
        distance_noise = 0.5 * (1 - np.exp(-distance / 100)) 
        self.qber = min(0.5, qber + distance_noise)

    def transmit(self, state):
        if np.random.random() < self.qber:
            # Apply bit flip noise
            return QuantumState([state.state[1], state.state[0]])
        return state

def measure(state, basis='Z'):
    """Measures a qubit in the specified basis ('Z' or 'X')."""
    if basis == 'Z':
        probs = np.abs(state.state)**2
    elif basis == 'X':
        h = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
        x_state = h @ state.state
        probs = np.abs(x_state)**2
    else:
        raise ValueError("Unsupported basis")
    
    result = np.random.choice([0, 1], p=probs)
    return result
