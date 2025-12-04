"""
Pollard's Kangaroo (Lambda) Algorithm for 4-bit ECDSA

This algorithm is optimal when you know the private key lies in a BOUNDED RANGE.
Instead of O(sqrt(N)) for the full group, it achieves O(sqrt(W)) where W is the
width of the search range.

USE CASES:
- Key is known to be in a specific range (e.g., from partial information leak)
- Searching for keys with specific bit patterns
- When you have side-channel information narrowing possibilities

RANGE SIZE VS STEPS:
    Range Width W    Expected Steps    Example Range
    ------------------------------------------------
    4                ~2                [0x0C, 0x0F]
    8                ~3                [0x08, 0x0F]
    16               ~4                [0x01, 0x10] (full 4-bit)
    256              ~16               8-bit key
    2^32             ~65536            32-bit key
    2^64             ~2^32             64-bit key (still feasible)
    2^128            ~2^64             128-bit (years)
    2^256            ~2^128            256-bit Bitcoin (heat death of universe)

The algorithm uses two "kangaroos":
- TAME kangaroo: starts at known point b*G (upper bound)
- WILD kangaroo: starts at target Q

Both take pseudorandom jumps. When they land on the same point (collision),
we can compute the discrete log from the difference in their "distances traveled".
"""

import sys
import os
import time
import math
import random
from typing import Tuple, Optional, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.rollbackMechanism import RollbackMechanism
from cryptography.ecdsa4bit import (
    p, A, B, G, N, INFINITY,
    point_multiply, point_add, mod_inverse, is_on_curve,
    to_hex, point_to_hex
)


class KangarooECDSA4bitMechanism(RollbackMechanism):
    """
    Pollard's Kangaroo algorithm for bounded-range discrete log.

    Optimal when private key is known to be in range [a, b].
    Time complexity: O(sqrt(b - a)) instead of O(sqrt(N))
    Space complexity: O(1) - only stores current positions
    """

    def __init__(self, target, key_range: Tuple[int, int] = None,
                 verbose=True, max_iterations=None):
        """
        Initialize the Kangaroo mechanism.

        Args:
            target: Target public key point (x, y)
            key_range: Tuple (a, b) where a <= private_key <= b
                      If None, uses full range [1, N-1]
            verbose: Print detailed output
            max_iterations: Safety limit on iterations
        """
        super().__init__(target)
        self.target = target
        self.verbose = verbose
        self.max_iterations = max_iterations

        # Set search range
        if key_range is None:
            self.range_start = 1
            self.range_end = N - 1
        else:
            self.range_start = max(1, key_range[0])
            self.range_end = min(N - 1, key_range[1])

        self.range_width = self.range_end - self.range_start + 1

        # Jump set - pseudorandom jumps of varying sizes
        # Mean jump size should be about sqrt(W)/2 for optimal performance
        self._setup_jump_set()

        self.stats = {
            'total_iterations': 0,
            'tame_steps': 0,
            'wild_steps': 0,
            'point_operations': 0,
            'found': False,
            'attack_type': 'pollard_kangaroo',
            'range_start': self.range_start,
            'range_end': self.range_end,
            'range_width': self.range_width,
            'expected_steps': int(math.sqrt(self.range_width) * 2),
            'time_elapsed': 0
        }

    def _setup_jump_set(self):
        """
        Set up the jump distances and precomputed jump points.

        For optimal performance, use powers of 2 up to sqrt(W).
        Mean jump should be approximately sqrt(W)/4.
        """
        # Number of different jump sizes
        k = max(2, int(math.log2(self.range_width + 1)))
        k = min(k, 8)  # Cap at 8 different jumps for small ranges

        # Jump distances: 1, 2, 4, 8, ... up to roughly sqrt(W)
        self.jump_distances = []
        self.jump_points = []  # Precomputed s_i * G

        for i in range(k):
            s_i = 1 << i  # 2^i
            if s_i > self.range_width:
                break
            self.jump_distances.append(s_i)
            self.jump_points.append(point_multiply(s_i, G))

        self.num_jumps = len(self.jump_distances)
        self.mean_jump = sum(self.jump_distances) / self.num_jumps

    def _hash_to_jump_index(self, point) -> int:
        """
        Deterministic function mapping point to jump index.
        Must be deterministic so tame and wild kangaroos make same
        jump when at same point.
        """
        if point is None:
            return 0
        # Use x-coordinate to select jump
        return point[0] % self.num_jumps

    def _jump(self, point, distance) -> Tuple:
        """
        Take one kangaroo jump.

        Args:
            point: Current point
            distance: Current total distance traveled

        Returns:
            (new_point, new_distance, jump_size)
        """
        self.stats['point_operations'] += 1

        idx = self._hash_to_jump_index(point)
        jump_size = self.jump_distances[idx]
        jump_point = self.jump_points[idx]

        new_point = point_add(point, jump_point)
        new_distance = distance + jump_size

        return new_point, new_distance, jump_size

    def print_stats(self):
        """Print algorithm statistics."""
        print("\n" + "=" * 70)
        print("KANGAROO ALGORITHM STATISTICS")
        print("=" * 70)
        print(f"Attack Type:            {self.stats['attack_type']}")
        print(f"Search Range:           [{to_hex(self.range_start)}, {to_hex(self.range_end)}]")
        print(f"Range Width:            {self.range_width}")
        print(f"Expected Steps:         ~{self.stats['expected_steps']} (sqrt({self.range_width}) * 2)")
        print(f"Actual Steps:           {self.stats['total_iterations']}")
        print(f"  Tame Kangaroo:        {self.stats['tame_steps']}")
        print(f"  Wild Kangaroo:        {self.stats['wild_steps']}")
        print(f"Point Operations:       {self.stats['point_operations']}")
        print(f"Time Elapsed:           {self.stats['time_elapsed']:.6f} seconds")
        print(f"Private Key Found:      {'Yes' if self.stats['found'] else 'No'}")
        print("=" * 70)

    def run(self):
        """
        Execute Pollard's Kangaroo algorithm.

        Returns:
            Dictionary containing results and statistics
        """
        start_time = time.time()

        if self.verbose:
            self._print_header()

        target_point = self._get_target_point()
        if target_point is None:
            print("Error: Cannot determine target point")
            return {'found': False, 'private_key': None, 'stats': self.stats}

        result = self._kangaroo_search(target_point)

        self.stats['time_elapsed'] = time.time() - start_time

        self.result = {
            'found': self.stats['found'],
            'private_key': result,
            'target': self.target,
            'stats': self.stats.copy()
        }

        if self.verbose:
            self.print_stats()
            if result is not None:
                print(f"\nResult: Private key = {to_hex(result)}")
                Q = point_multiply(result, G)
                print(f"Verify: {to_hex(result)} * G = {point_to_hex(Q)}")
                print(f"Match:  {Q == self.target}")

        return self.result

    def _print_header(self):
        """Print algorithm header."""
        print(f'\n{"=" * 70}')
        print("POLLARD'S KANGAROO (LAMBDA) ALGORITHM")
        print(f'{"=" * 70}')
        print()
        print(f'Target Q:     {point_to_hex(self.target)}')
        print(f'Search range: [{to_hex(self.range_start)}, {to_hex(self.range_end)}]')
        print(f'Range width:  {self.range_width}')
        print(f'Expected:     ~{int(math.sqrt(self.range_width) * 2)} steps')
        print()
        print(f'Jump set ({self.num_jumps} jumps):')
        for i, (dist, pt) in enumerate(zip(self.jump_distances, self.jump_points)):
            print(f'  s[{i}] = {dist:2d}, jump point = {point_to_hex(pt)}')
        print(f'Mean jump: {self.mean_jump:.1f}')

    def _kangaroo_search(self, target_point):
        """
        Run the kangaroo search.

        TAME kangaroo: Starts at b*G (upper bound of range)
        WILD kangaroo: Starts at Q (target point)

        Both take pseudorandom walks. If they collide, we can compute d.
        """
        if self.verbose:
            print(f'\n{"=" * 70}')
            print("KANGAROO SEARCH")
            print(f'{"=" * 70}')

        # Calculate how far each kangaroo should travel
        # Optimal: each travels about sqrt(W) * mean_jump
        travel_limit = int(math.sqrt(self.range_width) * self.mean_jump * 4)
        travel_limit = max(travel_limit, self.range_width)  # At least cover the range

        if self.verbose:
            print(f'\nTravel limit: {travel_limit}')

        # ===== TAME KANGAROO =====
        # Starts at known point: range_end * G
        # We know exactly where it is relative to G
        if self.verbose:
            print(f'\n[TAME KANGAROO]')
            print(f'  Starting at {to_hex(self.range_end)} * G')

        tame_point = point_multiply(self.range_end, G)
        tame_distance = 0  # Distance traveled from starting point

        # Store tame kangaroo's path for collision detection
        # In practice, use distinguished points; here we store all for small example
        tame_trail = {tame_point: tame_distance}

        # Let tame kangaroo run
        if self.verbose:
            print(f'  Initial: {point_to_hex(tame_point)}, dist=0')

        while tame_distance < travel_limit:
            self.stats['total_iterations'] += 1
            self.stats['tame_steps'] += 1

            tame_point, tame_distance, jump = self._jump(tame_point, tame_distance)
            tame_trail[tame_point] = tame_distance

            if self.verbose:
                print(f'  Jump +{jump}: {point_to_hex(tame_point)}, dist={tame_distance}')

            if self.max_iterations and self.stats['total_iterations'] >= self.max_iterations:
                break

        # ===== WILD KANGAROO =====
        # Starts at Q = d*G where d is unknown
        if self.verbose:
            print(f'\n[WILD KANGAROO]')
            print(f'  Starting at Q = {point_to_hex(target_point)}')

        wild_point = target_point
        wild_distance = 0

        if self.verbose:
            print(f'  Initial: {point_to_hex(wild_point)}, dist=0')

        # Wild kangaroo runs until it hits tame's trail
        while wild_distance < travel_limit:
            self.stats['total_iterations'] += 1
            self.stats['wild_steps'] += 1

            # Check for collision with tame trail
            if wild_point in tame_trail:
                tame_dist_at_collision = tame_trail[wild_point]

                if self.verbose:
                    print(f'\n  *** COLLISION DETECTED! ***')
                    print(f'  Wild at {point_to_hex(wild_point)} after {wild_distance} steps')
                    print(f'  Tame was here after {tame_dist_at_collision} steps')

                # At collision point:
                # Tame: (range_end + tame_dist) * G
                # Wild: (d + wild_dist) * G
                # These are equal, so:
                # range_end + tame_dist = d + wild_dist (mod N)
                # d = range_end + tame_dist - wild_dist (mod N)

                d = (self.range_end + tame_dist_at_collision - wild_distance) % N
                if d == 0:
                    d = N

                if self.verbose:
                    print(f'\n  Computing d:')
                    print(f'    d = range_end + tame_dist - wild_dist')
                    print(f'    d = {self.range_end} + {tame_dist_at_collision} - {wild_distance}')
                    print(f'    d = {d}')

                # Verify
                if point_multiply(d, G) == target_point:
                    self.stats['found'] = True
                    return d
                else:
                    if self.verbose:
                        print(f'  Verification failed, continuing...')

            wild_point, wild_distance, jump = self._jump(wild_point, wild_distance)

            if self.verbose:
                print(f'  Jump +{jump}: {point_to_hex(wild_point)}, dist={wild_distance}')

            if self.max_iterations and self.stats['total_iterations'] >= self.max_iterations:
                break

        return None

    def _get_target_point(self):
        """Extract target point from various input formats."""
        if isinstance(self.target, tuple) and len(self.target) == 2:
            return self.target
        elif isinstance(self.target, dict) and 'public_key' in self.target:
            return self.target['public_key']
        elif isinstance(self.target, dict) and 'Q' in self.target:
            return self.target['Q']
        return None


def demo():
    """Demonstrate Kangaroo algorithm with different range sizes."""
    print("\n" + "=" * 70)
    print("POLLARD'S KANGAROO - BOUNDED RANGE DEMONSTRATION")
    print("=" * 70)

    # Create a keypair where we "know" the key is in a range
    private_key = 0x0B  # 11 in decimal, binary: 1011
    public_key = point_multiply(private_key, G)

    print(f"\nSecret private key: d = {to_hex(private_key)} ({private_key} decimal)")
    print(f"Public key:         Q = {point_to_hex(public_key)}")

    # Test different range sizes
    test_ranges = [
        (0x0A, 0x0C, "Narrow: [0x0A, 0x0C] width=3"),
        (0x08, 0x0F, "Medium: [0x08, 0x0F] width=8"),
        (0x01, 0x12, "Full:   [0x01, 0x12] width=18 (all keys)"),
    ]

    print("\n" + "-" * 70)
    print("Testing different range sizes:")
    print("-" * 70)

    for range_start, range_end, description in test_ranges:
        print(f"\n>>> {description}")

        mechanism = KangarooECDSA4bitMechanism(
            public_key,
            key_range=(range_start, range_end),
            verbose=False
        )
        result = mechanism.run()

        if result['found']:
            stats = result['stats']
            print(f"    Found d = {to_hex(result['private_key'])}")
            print(f"    Steps: {stats['total_iterations']} "
                  f"(expected ~{stats['expected_steps']})")
            print(f"    Tame: {stats['tame_steps']}, Wild: {stats['wild_steps']}")
        else:
            print(f"    NOT FOUND")

    # Detailed run with verbose output
    print("\n" + "=" * 70)
    print("DETAILED RUN (narrow range)")
    print("=" * 70)

    mechanism = KangarooECDSA4bitMechanism(
        public_key,
        key_range=(0x09, 0x0D),  # Width of 5
        verbose=True
    )
    result = mechanism.run()

    print("\n" + "=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print("""
Kangaroo is optimal when you have PARTIAL INFORMATION about the key:

- Side-channel leak reveals some bits -> search remaining bits
- Key known to follow certain pattern -> restrict range
- Weak RNG limited key space -> exploit reduced entropy

For full 256-bit Bitcoin keys with no information:
  - Kangaroo: O(sqrt(2^256)) = O(2^128) steps
  - Same as Pollard's Rho (no advantage)

But if you know 128 bits of the key:
  - Kangaroo: O(sqrt(2^128)) = O(2^64) steps
  - Now feasible with enough compute!

This is why side-channel attacks + Kangaroo are dangerous together.
""")


if __name__ == "__main__":
    demo()
