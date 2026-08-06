import hashlib

import pandas as pd
import numpy as np

def cascade_error_correction(alice_bits, bob_bits, block_size=None):
    """
    Simulates the Cascade error correction protocol.
    In each pass, it identifies parity mismatches and corrects them.
    """
    alice_bits = np.array(alice_bits)
    bob_bits = np.array(bob_bits)
    
    if block_size is None:
        # Initial block size based on estimated error rate
        error_rate = np.sum(alice_bits != bob_bits) / len(alice_bits)
        block_size = int(1 / max(0.01, error_rate)) if error_rate > 0 else len(alice_bits)

    corrected_bob_bits = bob_bits.copy()
    passes = 4
    for p in range(passes):
        # Shuffle for different passes
        indices = np.arange(len(alice_bits))
        if p > 0:
            np.random.shuffle(indices)
        
        for i in range(0, len(alice_bits), block_size):
            block_idx = indices[i:i+block_size]
            if len(block_idx) == 0: continue
            
            alice_parity = np.sum(alice_bits[block_idx]) % 2
            bob_parity = np.sum(corrected_bob_bits[block_idx]) % 2
            
            if alice_parity != bob_parity:
                # Binary search to find the error in this block
                low = 0
                high = len(block_idx) - 1
                while low <= high:
                    mid = (low + high) // 2
                    sub_idx = block_idx[low:mid+1]
                    a_sub_parity = np.sum(alice_bits[sub_idx]) % 2
                    b_sub_parity = np.sum(corrected_bob_bits[sub_idx]) % 2
                    
                    if a_sub_parity != b_sub_parity:
                        if low == mid:
                            # Error found, flip it
                            corrected_bob_bits[block_idx[low]] = 1 - corrected_bob_bits[block_idx[low]]
                            break
                        high = mid
                    else:
                        low = mid + 1
        block_size *= 2 # Increase block size for next pass

    final_errors = np.sum(alice_bits != corrected_bob_bits)
    return corrected_bob_bits.tolist(), final_errors

def export_results_to_file(results, filename="simulation_results.csv"):
    """Exports simulation results to CSV or Excel."""
    # Convert lists to strings for easier viewing in CSV
    export_data = {}
    for k, v in results.items():
        if isinstance(v, list):
            export_data[k] = [str(v)]
        elif isinstance(v, dict):
            for sk, sv in v.items():
                export_data[f"{k}_{sk}"] = [sv]
        else:
            export_data[k] = [v]
            
    df = pd.DataFrame(export_data)
    if filename.endswith('.xlsx'):
        df.to_excel(filename, index=False)
    else:
        df.to_csv(filename, index=False)
    return filename

def privacy_amplification(bits):
    """
    Uses SHA-256 to generate a final secure key from the corrected bits.
    """
    bit_string = "".join(map(str, bits))
    hash_object = hashlib.sha256(bit_string.encode())
    return hash_object.hexdigest()
