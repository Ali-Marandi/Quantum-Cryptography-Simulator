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

class QuantumChannel:
    """Simulates a quantum channel with noise."""
    def __init__(self, qber=0.0):
        self.qber = qber

    def transmit(self, state):
        if np.random.random() < self.qber:
            # Apply bit flip noise
            return QuantumState([state.state[1], state.state[0]])
        return state

def measure(state, basis='Z'):
    """Measures a qubit in the specified basis ('Z' or 'X')."""
    if basis == 'Z':
        # Computational basis: |0>, |1>
        probs = np.abs(state.state)**2
    elif basis == 'X':
        # Hadamard basis: |+>, |->
        # Transformation matrix H = 1/sqrt(2) * [[1, 1], [1, -1]]
        h = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
        x_state = h @ state.state
        probs = np.abs(x_state)**2
    else:
        raise ValueError("Unsupported basis")
    
    result = np.random.choice([0, 1], p=probs)
    return result
