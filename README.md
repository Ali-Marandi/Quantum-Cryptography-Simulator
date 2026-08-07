# Quantum Cryptography Simulator (Enterprise Edition)

## Overview
This is a comprehensive, commercial-grade Quantum Cryptography Simulation and Experimentation Platform. It is designed for researchers, educators, and cybersecurity professionals to simulate advanced QKD protocols in realistic network environments.

## Enterprise Features (v2.x Strategic Edition)

### 0. Strategic v2.x Features
- **Satellite QKD (v2.0.0)**: Modeling atmospheric loss and satellite-to-ground quantum links.
- **AI Security (v2.1.0)**: ML-based eavesdropping detection using Anomaly Detection (Isolation Forest).
- **Quantum Messenger (v2.2.0)**: Real-world secure chat application using quantum-generated keys.
- **Simulation Database (v2.3.0)**: Local SQLite database for persistent simulation history and auditing.
- **City-scale View (v2.4.0)**: Metropolitan-scale network visualization for infrastructure planning.

### 1. Advanced Protocol Suite
- **BB84**: Standard 4-state protocol.
- **B92**: Two-state non-orthogonal protocol.
- **E91**: Entanglement-based Ekert91 protocol with Bell inequality verification.

### 2. Quantum Networking (v1.3.0)
- **Multi-node Topology**: Design networks with multiple end-nodes and repeaters.
- **Quantum Repeaters**: Simulate intermediate nodes for long-distance key distribution.
- **Key Routing**: Simplified XOR-based key routing across multiple hops.

### 3. Hardware Emulation (v1.4.0)
- **Photon Source Modeling**: Switch between Ideal Single Photon sources and Weak Coherent Pulses (WCP).
- **Detector Imperfections**: Configurable efficiency, dark count rates, and dead times.
- **Equipment Library**: Built-in profiles for industry-leading hardware like **ID Quantique** and **Toshiba**.

### 4. Advanced Attack Suite (v1.5.0)
- **PNS Attack**: Simulate Photon Number Splitting on WCP sources.
- **Detector Blinding**: Physical layer attacks on quantum detectors.
- **Security Score**: Automated penetration testing and real-time security rating.

### 5. Integration & Standards (v1.6.0)
- **Python SDK**: A professional API for integrating the simulation engine into other software.
- **ETSI GS QKD 014**: Generate compliance reports based on European telecommunications standards.

### 6. UX & EdTech (v1.7.0)
- **Bloch Sphere Visualization**: Real-time 3D rendering of quantum states.
- **Interactive Lab Mode**: Step-by-step guided tutorials for students.
- **Fiber Modeling**: QBER calculation based on fiber distance and attenuation.

## Installation & Usage
### Windows
Download the latest `QuantumCryptoSimulator.exe` from the [Releases](https://github.com/Ali-Marandi/Quantum-Cryptography-Simulator/releases) page.

### Python SDK
```python
from src.engine.sdk import QCryptoSDK
sdk = QCryptoSDK()
results = sdk.run_bb84(n_bits=500, qber=0.02)
print(results['qber'])
```

## Technologies Used
- **Python 3.12**
- **CustomTkinter**: Modern UI framework.
- **NumPy & SciPy**: High-performance physics simulation.
- **Matplotlib**: 2D/3D data visualization.
- **Pandas**: Data export and analysis.

## License
Enterprise Grade - All Rights Reserved.
