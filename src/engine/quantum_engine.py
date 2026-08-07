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

class PhotonSource:
    """Models different types of photon sources."""
    def __init__(self, source_type="SinglePhoton", mean_photon_number=0.1):
        self.source_type = source_type
        self.mu = mean_photon_number # Mean photon number for WCP

    def emit(self, state):
        if self.source_type == "WCP":
            # Poisson distribution for photon number
            n = np.random.poisson(self.mu)
            if n == 0: return None # Vacuum state
            return [state] * n # Multiple photons (PNS vulnerability)
        return [state]

class Detector:
    """Models quantum detectors with imperfections."""
    def __init__(self, efficiency=0.1, dark_count_rate=1e-5, dead_time=100e-9):
        self.efficiency = efficiency
        self.dark_count_rate = dark_count_rate
        self.dead_time = dead_time
        self.is_blinded = False

    def detect(self, state):
        if self.is_blinded:
            return None
        # Efficiency check
        if np.random.random() > self.efficiency:
            return None
        # Dark count check
        if np.random.random() < self.dark_count_rate:
            return np.random.randint(0, 2)
        return None 

class AttackSuite:
    """Collection of advanced quantum attacks."""
    @staticmethod
    def pns_attack(photons):
        """Photon Number Splitting attack."""
        if photons and len(photons) > 1:
            # Eve takes one photon and lets the rest go
            eve_photon = photons[0]
            remaining_photons = photons[1:]
            return eve_photon, remaining_photons
        return None, photons

    @staticmethod
    def detector_blinding(detector):
        """Blinds the detector using high-power pulses."""
        detector.is_blinded = True
        return True

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
        if state is None: return None
        if np.random.random() < self.qber:
            return QuantumState([state.state[1], state.state[0]])
        return state

class QuantumNode:
    """Represents a node in a quantum network."""
    def __init__(self, name, node_type="EndNode", pos=(0, 0, 0)):
        self.name = name
        self.node_type = node_type # EndNode, Repeater, or Satellite
        self.pos = pos # (x, y, z) coordinates
        self.keys = {} # Store keys shared with other nodes

class FreeSpaceChannel:
    """Simulates a free-space quantum channel (Satellite-to-Ground)."""
    def __init__(self, altitude=500, weather="Clear", turbulence="Low"):
        self.altitude = altitude # in km
        self.weather = weather
        self.turbulence = turbulence
        
        # Atmospheric loss modeling (Simplified)
        weather_loss = {"Clear": 0.1, "Cloudy": 0.5, "Foggy": 0.9}
        turbulence_noise = {"Low": 0.01, "Medium": 0.05, "High": 0.15}
        
        self.loss = weather_loss.get(weather, 0.1)
        self.qber = turbulence_noise.get(turbulence, 0.01) + (altitude / 5000)

    def transmit(self, state):
        if state is None: return None
        # Loss check
        if np.random.random() < self.loss:
            return None
        # Noise check
        if np.random.random() < self.qber:
            return QuantumState([state.state[1], state.state[0]])
        return state

class QuantumNetwork:
    """Manages a collection of nodes and channels."""
    def __init__(self):
        self.nodes = {}
        self.channels = []

    def add_node(self, name, node_type="EndNode", pos=None):
        if pos is None:
            pos = (np.random.uniform(0, 10), np.random.uniform(0, 10), np.random.uniform(0, 10))
        node = QuantumNode(name, node_type, pos)
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
