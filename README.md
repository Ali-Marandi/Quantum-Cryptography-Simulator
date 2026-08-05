# Quantum Cryptography Simulator (Commercial Edition)

## Overview
This is a professional-grade Quantum Cryptography Simulation and Experimentation Platform. It provides a robust environment for simulating, analyzing, and visualizing quantum key distribution (QKD) protocols with a modern, beautiful user interface.

## Key Features
- **Advanced Protocol Support**: Full implementation of the **BB84** protocol with support for B92 and E91 in development.
- **Realistic Channel Simulation**: Configurable Quantum Bit Error Rate (QBER) and environmental noise models.
- **Eavesdropping Analysis**: Simulate "Eve" with adjustable interception rates to test protocol security.
- **Post-Processing**: Integrated privacy amplification using SHA-256 hashing.
- **Interactive Dashboard**: Real-time visualization of key distribution statistics and error analysis.
- **Modern UI**: Built with a sleek dark-themed interface for professional use.

## Advanced Capabilities
- **Eve Detection**: Automatic detection of eavesdropping based on QBER threshold analysis.
- **Detailed Logging**: Step-by-step breakdown of Alice and Bob's bases, bits, and sifting process.
- **Security Metrics**: Live charts showing key generation efficiency and error rates.

## Installation & Usage
### Windows (Recommended)
Download the latest `QuantumCryptoSimulator.exe` from the [Releases](https://github.com/Ali-Marandi/Quantum-Cryptography-Simulator/releases) page.

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Ali-Marandi/Quantum-Cryptography-Simulator.git
   cd Quantum-Cryptography-Simulator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Technologies Used
- **Python 3.11**
- **CustomTkinter**: For the modern desktop UI.
- **NumPy**: For high-performance quantum state simulations.
- **Matplotlib**: For real-time data visualization.
- **PyInstaller**: For standalone Windows distribution.

## License
Commercial Grade - All Rights Reserved.
