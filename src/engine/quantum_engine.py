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
    def __init__(self, source_node, target_node, qber=0.0, distance=0.0, attenuation_coeff=0.2):
        self.source = source_node
        self.target = target_node
        self.distance = distance
        self.attenuation_coeff = attenuation_coeff
        distance_noise = 0.5 * (1 - np.exp(-distance / 100)) 
        self.qber = min(0.5, qber + distance_noise)

    def transmit(self, state):
        if np.random.random() < self.qber:
            return QuantumState([state.state[1], state.state[0]])
        return state

class QuantumNode:
    """Represents a node in a quantum network."""
    def __init__(self, name, node_type="EndNode"):
        self.name = name
        self.node_type = node_type # EndNode or Repeater
        self.keys = {} # Store keys shared with other nodes

class QuantumNetwork:
    """Manages a collection of nodes and channels."""
    def __init__(self):
        self.nodes = {}
        self.channels = []

    def add_node(self, name, node_type="EndNode"):
        node = QuantumNode(name, node_type)
        self.nodes[name] = node
        return node

    def add_channel(self, source_name, target_name, distance=10.0, qber=0.01):
        if source_name in self.nodes and target_name in self.nodes:
            channel = QuantumChannel(self.nodes[source_name], self.nodes[target_name], qber, distance)
            self.channels.append(channel)
            return channel
        return None

    def get_path(self, start_node, end_node):
        """Simple pathfinding for the network (BFS)."""
        # For now, we return a simple list of channels if they exist
        # In a real commercial app, this would be a full Dijkstra
        path = []
        for ch in self.channels:
            if ch.source.name == start_node and ch.target.name == end_node:
                path.append(ch)
                return path
        return None

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
