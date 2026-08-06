import numpy as np
import matplotlib.pyplot as plt
from src.engine.protocols import BB84Protocol
import os

def run_analysis():
    qber_values = np.linspace(0, 0.25, 11) # 0% to 25% QBER
    n_bits = 1000
    results = []

    for qber in qber_values:
        # Run without Eve
        protocol = BB84Protocol(n_bits=n_bits, qber=qber, eve_present=False)
        res = protocol.run()
        
        # Run with Eve (100% interception)
        protocol_eve = BB84Protocol(n_bits=n_bits, qber=qber, eve_present=True, eve_interception_rate=1.0)
        res_eve = protocol_eve.run()
        
        results.append({
            "qber": qber,
            "sifted_len": len(res["alice_sifted"]),
            "measured_qber": res["qber"],
            "measured_qber_eve": res_eve["qber"]
        })

    # Plotting
    qbers = [r["qber"] for r in results]
    sifted_lens = [r["sifted_len"] for r in results]
    measured_qbers = [r["measured_qber"] for r in results]
    measured_qbers_eve = [r["measured_qber_eve"] for r in results]

    plt.figure(figsize=(12, 5))

    # Plot 1: Sifted Key Length vs QBER
    plt.subplot(1, 2, 1)
    plt.plot(qbers, sifted_lens, 'bo-', label='Sifted Key Length')
    plt.xlabel('Input QBER')
    plt.ylabel('Sifted Key Length')
    plt.title('Sifted Key Length vs. Channel Noise')
    plt.grid(True)

    # Plot 2: Measured QBER vs Input QBER (With and Without Eve)
    plt.subplot(1, 2, 2)
    plt.plot(qbers, measured_qbers, 'g^-', label='Without Eve')
    plt.plot(qbers, measured_qbers_eve, 'rs-', label='With Eve (100% Intercept)')
    plt.axhline(y=0.11, color='gray', linestyle='--', label='Detection Threshold (11%)')
    plt.xlabel('Input QBER')
    plt.ylabel('Measured QBER')
    plt.title('Eve Detection Analysis')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('assets/bb84_performance.png')
    print("Analysis complete. Chart saved to assets/bb84_performance.png")

if __name__ == "__main__":
    if not os.path.exists('assets'):
        os.makedirs('assets')
    run_analysis()
