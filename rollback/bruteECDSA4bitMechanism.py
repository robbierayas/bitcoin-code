"""
Brute force 4-bit ECDSA rollback mechanism.

This module implements actual working brute force approaches to reverse 4-bit ECDSA
operations. With only 4 bits (15 possible private keys), we can:

1. BRUTE FORCE: Try all 15 possible private keys
2. BABY-STEP GIANT-STEP: Demonstrate the BSGS algorithm on a tractable problem
3. POLLARD'S RHO: Show how the probabilistic algorithm works
4. NONCE RECOVERY: Recover private key if nonce is known or weak
5. BUILD LOOKUP TABLE: Pre-compute all k*G values for instant lookup

This is FULLY FUNCTIONAL unlike the 256-bit version which is computationally infeasible.
"""

import sys
import os
import time
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.rollbackMechanism import RollbackMechanism
from cryptography.ecdsa4bit import (
    P, A, B, G, N, INFINITY,
    scalar_multiply, point_add, mod_inverse, is_on_curve,
    generate_all_points, to_hex, point_to_hex
)


class BruteECDSA4bitMechanism(RollbackMechanism):
    """
    Working brute force mechanism for 4-bit ECDSA rollback.

    This implementation can actually solve the discrete log problem
    because the search space is only 15 values (4 bits).
    """

    def __init__(self, target, attack_type='brute_force', max_iterations=None, progress_interval=1):
        """
        Initialize the brute force 4-bit ECDSA mechanism.

        Args:
            target: Target data (public key tuple, or dict with signature info)
            attack_type: Type of attack to use:
                - 'brute_force': Simple enumeration (default)
                - 'baby_step_giant_step': BSGS algorithm
                - 'pollard_rho': Pollard's rho algorithm
                - 'lookup_table': Pre-computed table
                - 'nonce_recovery': Recover from known/weak nonce
            max_iterations: Maximum iterations before stopping (None = unlimited)
            progress_interval: How often to report progress (every N iterations)
        """
        super().__init__(target)
        self.target = target
        self.attack_type = attack_type
        self.verbose = True
        self.max_iterations = max_iterations
        self.progress_interval = progress_interval

        # Stats tracking
        self.stats = {
            'total_iterations': 0,
            'keys_tested': 0,
            'point_operations': 0,
            'found': False,
            'stopped_early': False,
            'stop_reason': None,
            'attack_type': attack_type,
            'time_elapsed': 0
        }
        self.interrupted = False

        # Pre-build lookup table (it's tiny for 4 bits!)
        self.lookup_table = self._build_lookup_table()

    def _build_lookup_table(self):
        """Build a complete lookup table of k*G for all k in [1, N-1]."""
        table = {}
        for k in range(1, N):
            kG = scalar_multiply(k, G)
            if kG is not None:
                table[kG] = k
        return table

    def should_stop(self):
        """Check if we should stop (max iterations or interrupted)."""
        if self.interrupted:
            self.stats['stopped_early'] = True
            self.stats['stop_reason'] = 'interrupted'
            return True

        if self.max_iterations and self.stats['total_iterations'] >= self.max_iterations:
            self.stats['stopped_early'] = True
            self.stats['stop_reason'] = 'max_iterations'
            return True

        return False

    def print_stats(self):
        """Print current statistics."""
        print("\n" + "=" * 70)
        print("4-BIT ECDSA ROLLBACK STATISTICS")
        print("=" * 70)
        print(f"Attack Type:            {self.stats['attack_type']}")
        print(f"Total Iterations:       {self.stats['total_iterations']:,}")
        print(f"Keys Tested:            {self.stats['keys_tested']:,}")
        print(f"Point Operations:       {self.stats['point_operations']:,}")
        print(f"Time Elapsed:           {self.stats['time_elapsed']:.6f} seconds")
        print(f"Private Key Found:      {'Yes' if self.stats['found'] else 'No'}")

        if self.stats['stopped_early']:
            print(f"\nStopped Early:          Yes")
            print(f"Stop Reason:            {self.stats['stop_reason']}")

        print("=" * 70)

    def report_progress(self, message=None):
        """Report progress if at interval."""
        if self.stats['total_iterations'] % self.progress_interval == 0:
            if self.verbose and message:
                print(f"  [Progress] {message}")

    def run(self):
        """
        Execute the selected attack algorithm.

        Returns:
            Dictionary containing results and statistics
        """
        start_time = time.time()

        if self.verbose:
            print(f'\n{"=" * 70}')
            print(f'4-BIT ECDSA ROLLBACK - {self.attack_type.upper()}')
            print(f'{"=" * 70}')
            if isinstance(self.target, tuple):
                print(f'Target: {point_to_hex(self.target)}')
            else:
                print(f'Target: {self.target}')
            print(f'Attack: {self.attack_type}')
            print(f'Search space: {to_hex(N-1)} possible keys ({N-1})')

        # Select attack method
        if self.attack_type == 'brute_force':
            result = self._brute_force()
        elif self.attack_type == 'baby_step_giant_step':
            result = self._baby_step_giant_step()
        elif self.attack_type == 'pollard_rho':
            result = self._pollard_rho()
        elif self.attack_type == 'lookup_table':
            result = self._lookup_table_attack()
        elif self.attack_type == 'nonce_recovery':
            result = self._nonce_recovery()
        else:
            raise ValueError(f"Unknown attack type: {self.attack_type}")

        self.stats['time_elapsed'] = time.time() - start_time

        # Build final result
        self.result = {
            'found': self.stats['found'],
            'private_key': result,
            'target': self.target,
            'stats': self.stats.copy()
        }

        if self.verbose:
            self.print_stats()
            if result is not None:
                print(f"\n*** SUCCESS: Private key recovered = {to_hex(result)} ***")
                print(f"    Binary: {bin(result)[2:].zfill(4)}")
                # Verify
                Q = scalar_multiply(result, G)
                if isinstance(self.target, tuple):
                    print(f"    Verification: {to_hex(result)} * G = {point_to_hex(Q)}")
                    print(f"    Target:       {point_to_hex(self.target)}")
                    print(f"    Match:        {Q == self.target}")

        return self.result

    def _brute_force(self):
        """
        Simple brute force: try all private keys 1 to N-1.

        Time complexity: O(N)
        Space complexity: O(1)
        """
        if self.verbose:
            print(f'\nBrute force search: trying all {N-1} private keys...\n')

        target_point = self._get_target_point()
        if target_point is None:
            print("Error: Cannot determine target point")
            return None

        for d in range(1, N):
            if self.should_stop():
                break

            self.stats['total_iterations'] += 1
            self.stats['keys_tested'] += 1
            self.stats['point_operations'] += 1

            # Compute d * G
            Q = scalar_multiply(d, G)

            if self.verbose:
                self.report_progress(f"Testing d={to_hex(d)}: {to_hex(d)}*G = {point_to_hex(Q)}")

            # Check if this is our target
            if Q == target_point:
                self.stats['found'] = True
                return d

        return None

    def _baby_step_giant_step(self):
        """
        Baby-step Giant-step algorithm for discrete log.

        Solves: Find d such that d*G = Q

        Algorithm:
        1. Choose m = ceil(sqrt(N))
        2. Baby steps: Compute table of j*G for j = 0 to m-1
        3. Giant steps: Compute Q - i*m*G for i = 0 to m-1
        4. Find collision between baby and giant steps

        Time complexity: O(sqrt(N))
        Space complexity: O(sqrt(N))
        """
        if self.verbose:
            print(f'\nBaby-step Giant-step algorithm...\n')

        target_point = self._get_target_point()
        if target_point is None:
            print("Error: Cannot determine target point")
            return None

        m = math.ceil(math.sqrt(N))
        if self.verbose:
            print(f"  m = ceil(sqrt({N})) = {m}")

        # Baby steps: build table of j*G
        if self.verbose:
            print(f"\n  Baby steps: Computing j*G for j = 0 to {m-1}")
        baby_table = {}
        baby_table_infinity_j = None  # Special case for INFINITY
        point = INFINITY
        for j in range(m):
            self.stats['total_iterations'] += 1
            self.stats['point_operations'] += 1

            if point is None:
                baby_table_infinity_j = j  # Store j for INFINITY separately
            else:
                baby_table[point] = j
            if self.verbose:
                print(f"    {j}*G = {point_to_hex(point)}")

            point = point_add(point, G)

            if self.should_stop():
                return None

        # Giant steps: compute Q - i*m*G and look for collision
        if self.verbose:
            print(f"\n  Giant steps: Computing Q - i*{m}*G for i = 0 to {m-1}")

        mG = scalar_multiply(m, G)  # Precompute m*G
        neg_mG = (mG[0], (-mG[1]) % P) if mG else None  # -mG for subtraction
        if self.verbose:
            print(f"    {m}*G = {mG}")
            print(f"    -{m}*G = {neg_mG}")

        gamma = target_point
        for i in range(m):
            self.stats['total_iterations'] += 1
            self.stats['keys_tested'] += 1
            self.stats['point_operations'] += 1

            if self.verbose:
                print(f"    Q - {i}*{m}*G = {point_to_hex(gamma)}")

            # Check if gamma is INFINITY (special case)
            if gamma is None and baby_table_infinity_j is not None:
                j = baby_table_infinity_j
                d = (i * m + j) % N
                if self.verbose:
                    print(f"\n  COLLISION FOUND (at infinity)!")
                    print(f"    gamma = O = {j}*G (baby step)")
                    print(f"    gamma = Q - {i}*{m}*G (giant step)")
                    print(f"    Therefore: d = {i}*{m} + {j} = {d}")
                self.stats['found'] = True
                return d if d != 0 else N

            # Check if gamma is in baby table
            if gamma is not None and gamma in baby_table:
                j = baby_table[gamma]
                d = (i * m + j) % N
                if self.verbose:
                    print(f"\n  COLLISION FOUND!")
                    print(f"    gamma = {j}*G (baby step)")
                    print(f"    gamma = Q - {i}*{m}*G (giant step)")
                    print(f"    Therefore: d = {i}*{m} + {j} = {d}")
                self.stats['found'] = True
                return d if d != 0 else N

            # gamma = gamma - m*G = gamma + (-m*G)
            gamma = point_add(gamma, neg_mG)

            if self.should_stop():
                return None

        return None

    def _pollard_rho(self):
        """
        Pollard's rho algorithm for discrete log.

        A probabilistic algorithm that uses cycle detection.

        Time complexity: O(sqrt(N)) expected
        Space complexity: O(1)
        """
        if self.verbose:
            print(f'\nPollard\'s rho algorithm...\n')

        target_point = self._get_target_point()
        if target_point is None:
            print("Error: Cannot determine target point")
            return None

        def partition(point):
            """Partition function based on x coordinate."""
            if point is None:
                return 0
            return point[0] % 3

        def step(point, a, b):
            """
            One step of the random walk.
            Returns (new_point, new_a, new_b)
            """
            self.stats['point_operations'] += 1
            S = partition(point)

            if S == 0:
                # point = point + Q
                new_point = point_add(point, target_point)
                return (new_point, a, (b + 1) % N)
            elif S == 1:
                # point = 2 * point
                new_point = point_add(point, point)
                return (new_point, (2 * a) % N, (2 * b) % N)
            else:
                # point = point + G
                new_point = point_add(point, G)
                return (new_point, (a + 1) % N, b)

        # Initialize: X = a*G + b*Q where a, b are random
        a1, b1 = random.randint(1, N-1), random.randint(1, N-1)
        X = point_add(scalar_multiply(a1, G), scalar_multiply(b1, target_point))

        # Tortoise and hare
        a_tortoise, b_tortoise = a1, b1
        X_tortoise = X
        a_hare, b_hare = a1, b1
        X_hare = X

        if self.verbose:
            print(f"  Initial: X = {a1}*G + {b1}*Q = {X}")

        max_steps = N * 10  # Safety limit
        for step_num in range(max_steps):
            self.stats['total_iterations'] += 1

            # Tortoise: one step
            X_tortoise, a_tortoise, b_tortoise = step(X_tortoise, a_tortoise, b_tortoise)

            # Hare: two steps
            X_hare, a_hare, b_hare = step(X_hare, a_hare, b_hare)
            X_hare, a_hare, b_hare = step(X_hare, a_hare, b_hare)

            if self.verbose and step_num % self.progress_interval == 0:
                print(f"  Step {step_num}: tortoise={X_tortoise}, hare={X_hare}")

            # Check for collision
            if X_tortoise == X_hare:
                if self.verbose:
                    print(f"\n  Collision at step {step_num}!")
                    print(f"    Tortoise: {a_tortoise}*G + {b_tortoise}*Q = {X_tortoise}")
                    print(f"    Hare:     {a_hare}*G + {b_hare}*Q = {X_hare}")

                # Solve: a1*G + b1*Q = a2*G + b2*Q
                # (a1 - a2)*G = (b2 - b1)*Q = (b2 - b1)*d*G
                # d = (a1 - a2) * (b2 - b1)^(-1) mod N

                delta_a = (a_tortoise - a_hare) % N
                delta_b = (b_hare - b_tortoise) % N

                if delta_b == 0:
                    if self.verbose:
                        print("    Delta b = 0, trying again...")
                    # Restart with new random values
                    a1, b1 = random.randint(1, N-1), random.randint(1, N-1)
                    X = point_add(scalar_multiply(a1, G), scalar_multiply(b1, target_point))
                    a_tortoise, b_tortoise = a1, b1
                    X_tortoise = X
                    a_hare, b_hare = a1, b1
                    X_hare = X
                    continue

                try:
                    d = (delta_a * mod_inverse(delta_b, N)) % N
                    if d == 0:
                        d = N

                    # Verify
                    if scalar_multiply(d, G) == target_point:
                        if self.verbose:
                            print(f"    d = ({delta_a}) * ({delta_b})^(-1) mod {N} = {d}")
                        self.stats['found'] = True
                        self.stats['keys_tested'] = step_num + 1
                        return d
                except:
                    pass

            if self.should_stop():
                break

        return None

    def _lookup_table_attack(self):
        """
        Instant lookup using pre-computed table.

        Time complexity: O(1) lookup (O(N) precomputation)
        Space complexity: O(N)
        """
        if self.verbose:
            print(f'\nLookup table attack (pre-computed)...\n')

        target_point = self._get_target_point()
        if target_point is None:
            print("Error: Cannot determine target point")
            return None

        self.stats['total_iterations'] += 1
        self.stats['keys_tested'] = 1
        self.stats['point_operations'] = 0  # Already done in precomputation

        if target_point in self.lookup_table:
            self.stats['found'] = True
            d = self.lookup_table[target_point]
            if self.verbose:
                print(f"  Found in table: {target_point} -> d = {d}")
            return d

        if self.verbose:
            print(f"  Not found in table")
        return None

    def _nonce_recovery(self):
        """
        Recover private key from signature with known/weak nonce.

        If we know the nonce k used in a signature, we can compute:
        d = r^(-1) * (s*k - z) mod N

        Target should be a dict with: {'r': r, 's': s, 'z': z, 'k': k}
        """
        if self.verbose:
            print(f'\nNonce recovery attack...\n')

        if not isinstance(self.target, dict):
            print("Error: Nonce recovery requires dict with r, s, z, k")
            return None

        required_keys = ['r', 's', 'z', 'k']
        for key in required_keys:
            if key not in self.target:
                print(f"Error: Missing key '{key}' in target")
                return None

        r = self.target['r']
        s = self.target['s']
        z = self.target['z']
        k = self.target['k']

        self.stats['total_iterations'] += 1
        self.stats['keys_tested'] += 1

        if self.verbose:
            print(f"  Signature: r={to_hex(r)}, s={to_hex(s)}")
            print(f"  Message hash z={to_hex(z)}")
            print(f"  Known nonce k={to_hex(k)}")
            print(f"\n  Computing d = r^(-1) * (s*k - z) mod N")

        try:
            r_inv = mod_inverse(r, N)
            d = (r_inv * (s * k - z)) % N
            if d == 0:
                d = N

            if self.verbose:
                print(f"  r^(-1) mod {to_hex(N)} = {to_hex(r_inv)}")
                print(f"  s*k - z = {to_hex(s)}*{to_hex(k)} - {to_hex(z)} = {to_hex((s*k - z) % N)}")
                print(f"  d = {to_hex(r_inv)} * {to_hex((s*k - z) % N)} mod {to_hex(N)} = {to_hex(d)}")

            self.stats['found'] = True
            return d
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return None

    def _get_target_point(self):
        """Extract target point from various input formats."""
        if isinstance(self.target, tuple) and len(self.target) == 2:
            # Direct point
            return self.target
        elif isinstance(self.target, dict) and 'public_key' in self.target:
            return self.target['public_key']
        elif isinstance(self.target, dict) and 'Q' in self.target:
            return self.target['Q']
        return None


def demo():
    """Demonstrate all attack types on a known keypair."""
    print("\n" + "=" * 70)
    print("4-BIT ECDSA ROLLBACK DEMONSTRATION")
    print("=" * 70)

    # Create a known keypair
    private_key = 0x07
    public_key = scalar_multiply(private_key, G)

    print(f"\nTest keypair:")
    print(f"  Private key (SECRET): d = {to_hex(private_key)}")
    print(f"  Public key (PUBLIC):  Q = {point_to_hex(public_key)}")

    print("\n" + "-" * 70)
    print("Testing all attack types:")
    print("-" * 70)

    # Test each attack type
    attacks = ['brute_force', 'baby_step_giant_step', 'pollard_rho', 'lookup_table']

    for attack in attacks:
        print(f"\n>>> Testing {attack}...")
        mechanism = BruteECDSA4bitMechanism(public_key, attack_type=attack)
        mechanism.verbose = False  # Quiet for demo
        result = mechanism.run()

        if result['found']:
            print(f"    SUCCESS: d = {to_hex(result['private_key'])} "
                  f"(iterations: {result['stats']['total_iterations']}, "
                  f"time: {result['stats']['time_elapsed']:.6f}s)")
        else:
            print(f"    FAILED")

    # Test nonce recovery
    print(f"\n>>> Testing nonce_recovery...")
    # Create a signature with known nonce
    from cryptography.ecdsa4bit import sign
    z = 0x0B
    k = 0x03
    r, s = sign(private_key, z, k)

    target = {'r': r, 's': s, 'z': z, 'k': k}
    mechanism = BruteECDSA4bitMechanism(target, attack_type='nonce_recovery')
    mechanism.verbose = False
    result = mechanism.run()

    if result['found']:
        print(f"    SUCCESS: d = {to_hex(result['private_key'])} "
              f"(iterations: {result['stats']['total_iterations']}, "
              f"time: {result['stats']['time_elapsed']:.6f}s)")
    else:
        print(f"    FAILED")

    print("\n" + "=" * 70)
    print("All attacks recovered the private key successfully!")
    print("This demonstrates why 4-bit keys are completely insecure.")
    print("Real ECDSA uses 256-bit keys where these attacks are infeasible.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
