"""
Example: 4-bit ECDSA Rollback

Simple example showing how to use RollbackECDSA4bit to recover
a private key from a public key using various attack methods:

- Brute Force: Try all possible keys
- Baby-Step Giant-Step: O(sqrt(N)) classical algorithm
- Pollard's Rho: Probabilistic O(sqrt(N)) algorithm
- Lookup Table: Pre-computed instant lookup
- Nonce Recovery: Recover key from known nonce
- Shor's Algorithm: Quantum computing simulation

This is a placeholder pattern similar to how the full ECDSA
rollback would work - but this one actually succeeds because
the search space is only 15 possible keys (4 bits).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.rollbackECDSA4bit import RollbackECDSA4bit
from rollback.shorECDSA4bitMechanism import ShorECDSA4bitMechanism
from cryptography.ecdsa4bit import (
    generate_keypair, sign, to_hex, point_to_hex, scalar_multiply, G
)


def example_public_key_rollback():
    """
    Example: Recover private key from public key.

    Given only the public key Q, find private key d such that Q = d * G
    """
    print("=" * 70)
    print("EXAMPLE: Recover Private Key from Public Key")
    print("=" * 70)

    # Create a keypair (we'll pretend we only know the public key)
    d, Q = generate_keypair(0x07)

    print(f"\n[Setup] Created keypair:")
    print(f"  Private key d = {to_hex(d)} (this is SECRET)")
    print(f"  Public key  Q = {point_to_hex(Q)} (this is PUBLIC)")

    print(f"\n[Attack] Given only Q, attempting to find d...")

    # Use RollbackECDSA4bit to recover the private key
    rollback = RollbackECDSA4bit(Q, attack_type='brute_force', verbose=True)
    result = rollback.run()

    if result['found']:
        recovered_d = result['private_key']
        print(f"\n[Result] Recovered private key: {to_hex(recovered_d)}")
        print(f"[Verify] Match original: {recovered_d == d}")
    else:
        print("\n[Result] Failed to recover private key")


def example_nonce_recovery():
    """
    Example: Recover private key from signature with known nonce.

    If the nonce k is known (or leaked), the private key can be computed:
    d = r^(-1) * (s*k - z) mod N
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Recover Private Key from Known Nonce")
    print("=" * 70)

    # Create keypair and sign a message
    d = 0x07
    _, Q = generate_keypair(d)
    z = 0x0B  # message hash
    k = 0x03  # nonce (in real ECDSA this MUST be secret!)

    r, s = sign(d, z, k)

    print(f"\n[Setup] Signature created:")
    print(f"  Private key d = {to_hex(d)} (SECRET)")
    print(f"  Message hash z = {to_hex(z)}")
    print(f"  Nonce k = {to_hex(k)} (LEAKED!)")
    print(f"  Signature (r, s) = ({to_hex(r)}, {to_hex(s)})")

    print(f"\n[Attack] Nonce is known, computing d...")

    # Build target dict for nonce recovery
    target = {'r': r, 's': s, 'z': z, 'k': k}

    rollback = RollbackECDSA4bit(target, attack_type='nonce_recovery', verbose=True)
    result = rollback.run()

    if result['found']:
        recovered_d = result['private_key']
        print(f"\n[Result] Recovered private key: {to_hex(recovered_d)}")
        print(f"[Verify] Match original: {recovered_d == d}")


def example_compare_attacks():
    """
    Example: Compare all attack methods.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Compare Attack Methods")
    print("=" * 70)

    d, Q = generate_keypair(0x0A)
    print(f"\n[Target] Public key Q = {point_to_hex(Q)}")

    RollbackECDSA4bit.compare_attacks(Q)


def example_shor_algorithm():
    """
    Example: Shor's Quantum Algorithm Simulation.

    Demonstrates how a quantum computer would solve the discrete log problem
    using Shor's algorithm. This is a classical SIMULATION - we can do this
    because 4 bits is small enough to enumerate all quantum states.

    In real quantum computing:
    - All possible d values exist in SUPERPOSITION simultaneously
    - Quantum Fourier Transform detects PERIODICITY in the group structure
    - Measurement COLLAPSES to the correct answer with high probability

    Time complexity:
    - Classical brute force: O(N) = O(2^n)
    - Shor's algorithm: O(n³) = polynomial!

    For Bitcoin's 256-bit ECDSA:
    - Classical: 2^256 operations (impossible)
    - Quantum: ~256³ ≈ 16 million operations (with ~4000 qubits)
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Shor's Quantum Algorithm Simulation")
    print("=" * 70)

    # Create a keypair
    d = 0x0B  # Private key: 1011 in binary
    Q = scalar_multiply(d, G)

    print(f"\n[Setup] Created keypair:")
    print(f"  Private key d = {to_hex(d)} (this is SECRET)")
    print(f"  Public key  Q = {point_to_hex(Q)} (this is PUBLIC)")

    print(f"\n[Attack] Running Shor's algorithm simulation...")
    print("  (Simulating quantum superposition, QFT, and measurement)")

    # Run Shor's algorithm simulation
    shor = ShorECDSA4bitMechanism(Q, verbose=True, show_quantum_state=False)
    result = shor.run()

    if result['found']:
        recovered_d = result['private_key']
        print(f"\n[Result] Quantum attack recovered private key: {to_hex(recovered_d)}")
        print(f"[Verify] Match original: {recovered_d == d}")
    else:
        print("\n[Result] Failed to recover private key")

    # Print key insight
    print("\n" + "-" * 70)
    print("KEY INSIGHT:")
    print("-" * 70)
    print("""
  Classical Computer:
    - Must try keys one at a time: d=1, d=2, d=3, ...
    - Time: O(2^n) for n-bit keys
    - For 256 bits: 2^256 operations (heat death of universe!)

  Quantum Computer (Shor's Algorithm):
    - Tests ALL keys SIMULTANEOUSLY via superposition
    - QFT extracts the answer from interference patterns
    - Time: O(n³) for n-bit keys
    - For 256 bits: ~16 million operations (feasible!)

  Current Status (2024):
    - Largest quantum computers: ~1000 noisy qubits
    - Breaking Bitcoin ECDSA needs: ~4000 logical qubits
    - With error correction: millions of physical qubits
    - Timeline: Estimated 10-20 years
    """)


def main():
    """Run all examples."""
    example_public_key_rollback()
    example_nonce_recovery()
    example_compare_attacks()
    example_shor_algorithm()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
