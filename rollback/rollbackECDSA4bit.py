"""
4-bit ECDSA Rollback Interface.

This module provides a high-level interface for reversing 4-bit ECDSA operations.
Unlike the full 256-bit ECDSA, this is completely solvable and serves as an
educational tool for understanding ECDSA attacks.

Available attacks:
- brute_force: Try all 15 possible private keys
- baby_step_giant_step: Demonstrate BSGS algorithm
- pollard_rho: Probabilistic cycle-finding algorithm
- lookup_table: Instant lookup from pre-computed table
- nonce_recovery: Recover key from known/weak nonce
"""

import sys
import os
import signal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.bruteECDSA4bitMechanism import BruteECDSA4bitMechanism
from cryptography.ecdsa4bit import (
    G, N, scalar_multiply, sign, verify, generate_keypair,
    to_hex, point_to_hex
)


class RollbackECDSA4bit:
    """
    High-level interface for 4-bit ECDSA rollback operations.

    This class provides a clean API for reversing 4-bit ECDSA operations.
    All attacks actually work because the search space is only 15 values!

    Example usage:
        # Recover private key from public key
        rollback = RollbackECDSA4bit(public_key=(6, 3))
        result = rollback.run()
        print(f"Private key: {result['private_key']}")

        # Use specific attack type
        rollback = RollbackECDSA4bit((6, 3), attack_type='baby_step_giant_step')
        result = rollback.run()
    """

    ATTACK_TYPES = [
        'brute_force',
        'baby_step_giant_step',
        'pollard_rho',
        'lookup_table',
        'nonce_recovery'
    ]

    def __init__(self, target, attack_type='brute_force', verbose=True):
        """
        Initialize the 4-bit ECDSA rollback interface.

        Args:
            target: Target data for rollback. Can be:
                - tuple: Public key point (x, y)
                - dict: {'public_key': (x, y)} or {'Q': (x, y)}
                - dict: {'r': r, 's': s, 'z': z, 'k': k} for nonce recovery
            attack_type: Type of attack to use (default: 'brute_force')
                - 'brute_force': Simple enumeration O(N)
                - 'baby_step_giant_step': BSGS O(sqrt(N))
                - 'pollard_rho': Probabilistic O(sqrt(N))
                - 'lookup_table': Instant lookup O(1)
                - 'nonce_recovery': From known nonce
            verbose: Whether to print detailed output
        """
        if attack_type not in self.ATTACK_TYPES:
            raise ValueError(f"Unknown attack type: {attack_type}. "
                           f"Choose from: {self.ATTACK_TYPES}")

        self.target = target
        self.attack_type = attack_type
        self.verbose = verbose
        self.mechanism = None
        self.result = None

        # Initialize the mechanism
        self.mechanism = BruteECDSA4bitMechanism(
            target,
            attack_type=attack_type
        )
        self.mechanism.verbose = verbose

    def rollback(self, handle_interrupt=True):
        """
        Perform the rollback operation.

        This method executes the rollback mechanism and stores the result.
        Supports graceful interruption with Ctrl+C.

        Args:
            handle_interrupt: Whether to install Ctrl+C handler (default: True)

        Returns:
            Dictionary with:
                - 'found': bool - whether private key was found
                - 'private_key': int or None - the recovered key
                - 'target': the original target
                - 'stats': dict with timing and iteration stats
        """
        if self.mechanism is None:
            raise RuntimeError("No mechanism initialized")

        # Set up signal handler for graceful interruption
        old_handler = None
        if handle_interrupt:
            def signal_handler(sig, frame):
                print("\n\n[!] Interrupted by user (Ctrl+C)")
                print("Stopping gracefully...\n")
                self.mechanism.interrupted = True

            old_handler = signal.signal(signal.SIGINT, signal_handler)

        try:
            self.result = self.mechanism.run()
        finally:
            # Restore old signal handler
            if handle_interrupt and old_handler is not None:
                signal.signal(signal.SIGINT, old_handler)

        return self.result

    def run(self):
        """Execute the rollback (alias for rollback())."""
        return self.rollback()

    def get_result(self):
        """Get the result of the last rollback operation."""
        return self.result

    def set_verbose(self, verbose):
        """Set verbosity of the mechanism."""
        self.verbose = verbose
        if self.mechanism:
            self.mechanism.verbose = verbose

    @staticmethod
    def create_test_keypair(private_key=None):
        """
        Create a test keypair for experimentation.

        Args:
            private_key: Optional specific private key (1-15).
                        If None, uses 7 as default.

        Returns:
            tuple: (private_key, public_key)
        """
        if private_key is None:
            private_key = 7

        return generate_keypair(private_key)

    @staticmethod
    def create_test_signature(private_key, message_hash, nonce=None):
        """
        Create a test signature for nonce recovery experiments.

        Args:
            private_key: The private key to sign with
            message_hash: Hash of message to sign
            nonce: Optional specific nonce (if None, uses 3)

        Returns:
            dict: {'r': r, 's': s, 'z': z, 'k': k}
        """
        if nonce is None:
            nonce = 3

        r, s = sign(private_key, message_hash, nonce)
        return {
            'r': r,
            's': s,
            'z': message_hash,
            'k': nonce
        }

    @staticmethod
    def compare_attacks(public_key):
        """
        Compare all attack types on a given public key.

        Args:
            public_key: Target public key point (x, y)

        Returns:
            dict: Results for each attack type
        """
        results = {}

        attacks = ['brute_force', 'baby_step_giant_step', 'pollard_rho', 'lookup_table']

        print("\n" + "=" * 70)
        print("ATTACK COMPARISON")
        print("=" * 70)
        print(f"\nTarget public key: {point_to_hex(public_key)}")
        print("\n{:<25} {:>10} {:>12} {:>10}".format(
            "Attack", "Found", "Iterations", "Time (s)"))
        print("-" * 60)

        for attack in attacks:
            rollback = RollbackECDSA4bit(public_key, attack_type=attack, verbose=False)
            result = rollback.run()
            results[attack] = result

            found = "Yes" if result['found'] else "No"
            iterations = result['stats']['total_iterations']
            time_elapsed = result['stats']['time_elapsed']

            print(f"{attack:<25} {found:>10} {iterations:>12} {time_elapsed:>10.6f}")

        print("-" * 60)

        # Find best attack
        found_results = {k: v for k, v in results.items() if v['found']}
        if found_results:
            fastest = min(found_results.items(),
                         key=lambda x: x[1]['stats']['time_elapsed'])
            print(f"\nFastest attack: {fastest[0]} ({fastest[1]['stats']['time_elapsed']:.6f}s)")

        return results


def demo():
    """Demonstrate the rollback interface."""
    print("\n" + "=" * 70)
    print("4-BIT ECDSA ROLLBACK INTERFACE DEMO")
    print("=" * 70)

    # Create a test keypair
    private_key, public_key = RollbackECDSA4bit.create_test_keypair(0x07)
    print(f"\nTest keypair:")
    print(f"  Private key: {to_hex(private_key)} (binary: {bin(private_key)[2:].zfill(4)})")
    print(f"  Public key:  {point_to_hex(public_key)}")

    # Basic usage
    print("\n" + "-" * 70)
    print("Basic Usage: Recover private key from public key")
    print("-" * 70)

    rollback = RollbackECDSA4bit(public_key)
    result = rollback.run()

    if result['found']:
        print(f"\nRecovered private key: {to_hex(result['private_key'])}")
        print(f"Matches original: {result['private_key'] == private_key}")

    # Test nonce recovery
    print("\n" + "-" * 70)
    print("Nonce Recovery: Recover from known nonce")
    print("-" * 70)

    sig_data = RollbackECDSA4bit.create_test_signature(private_key, 0x0B, nonce=0x03)
    print(f"\nSignature data:")
    print(f"  r = {to_hex(sig_data['r'])}")
    print(f"  s = {to_hex(sig_data['s'])}")
    print(f"  z (message hash) = {to_hex(sig_data['z'])}")
    print(f"  k (nonce) = {to_hex(sig_data['k'])}")

    rollback = RollbackECDSA4bit(sig_data, attack_type='nonce_recovery')
    result = rollback.run()

    if result['found']:
        print(f"\nRecovered private key: {to_hex(result['private_key'])}")
        print(f"Matches original: {result['private_key'] == private_key}")

    # Compare all attacks
    print("\n" + "-" * 70)
    print("Attack Comparison")
    print("-" * 70)

    RollbackECDSA4bit.compare_attacks(public_key)

    print("\n" + "=" * 70)
    print("END OF DEMO")
    print("=" * 70)


if __name__ == "__main__":
    demo()
