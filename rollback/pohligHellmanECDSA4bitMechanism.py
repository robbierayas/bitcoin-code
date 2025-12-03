"""
Pohlig-Hellman Algorithm for 4-bit ECDSA

The Pohlig-Hellman algorithm exploits GROUP ORDER FACTORIZATION to solve
the discrete logarithm problem more efficiently when the group order N
has small prime factors.

HOW IT WORKS:
If N = p1^e1 * p2^e2 * ... * pk^ek, then:
1. Solve DLP modulo each prime power p_i^e_i separately
2. Combine solutions using Chinese Remainder Theorem

EXAMPLE:
If N = 12 = 4 * 3 = 2^2 * 3, we:
1. Find d mod 4 (only 4 possibilities)
2. Find d mod 3 (only 3 possibilities)
3. Combine: d mod 12 via CRT

Instead of 12 operations, we do 4 + 3 = 7 operations!

SECURITY IMPLICATIONS:
- Safe curves have N = large_prime (no small factors)
- If N has small factors, Pohlig-Hellman breaks it easily
- "Smooth" numbers (many small factors) are especially weak

YOUR 4-BIT CURVE:
- N = 19 (prime!) - Pohlig-Hellman doesn't help here
- But this code demonstrates the algorithm for education
- We include an example with a "bad" smooth-order curve
"""

import sys
import os
import time
import math
from typing import Tuple, Optional, Dict, List
from functools import reduce

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.rollbackMechanism import RollbackMechanism
from cryptography.ecdsa4bit import (
    P, A, B, G, N, INFINITY,
    scalar_multiply, point_add, mod_inverse, is_on_curve,
    to_hex, point_to_hex
)


def factor(n: int) -> List[Tuple[int, int]]:
    """
    Factor n into prime powers.

    Returns list of (prime, exponent) tuples.
    Example: factor(12) = [(2, 2), (3, 1)]  meaning 12 = 2^2 * 3^1
    """
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            exp = 0
            while temp % d == 0:
                exp += 1
                temp //= d
            factors.append((d, exp))
        d += 1
    if temp > 1:
        factors.append((temp, 1))
    return factors


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) where ax + by = gcd."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> int:
    """
    Chinese Remainder Theorem.

    Given:
        x = r1 (mod m1)
        x = r2 (mod m2)
        ...
        x = rk (mod mk)

    Returns x (mod m1*m2*...*mk) assuming moduli are pairwise coprime.
    """
    if len(remainders) == 0:
        return 0
    if len(remainders) == 1:
        return remainders[0] % moduli[0]

    # Product of all moduli
    M = reduce(lambda a, b: a * b, moduli, 1)

    result = 0
    for r_i, m_i in zip(remainders, moduli):
        M_i = M // m_i
        _, _, y_i = extended_gcd(m_i, M_i)
        result += r_i * y_i * M_i

    return result % M


class PohligHellmanECDSA4bitMechanism(RollbackMechanism):
    """
    Pohlig-Hellman algorithm for discrete log when group order factors.

    Time complexity: O(sum(e_i * (sqrt(p_i) + log(p_i))))
    where N = product(p_i^e_i)

    Much faster than O(sqrt(N)) when N has small factors!
    """

    def __init__(self, target, group_order=None, generator=None, verbose=True):
        """
        Initialize Pohlig-Hellman mechanism.

        Args:
            target: Target public key point (x, y)
            group_order: Order of the group (default: N from curve)
            generator: Generator point (default: G from curve)
            verbose: Print detailed output
        """
        super().__init__(target)
        self.target = target
        self.verbose = verbose
        self.group_order = group_order if group_order else N
        self.generator = generator if generator else G

        # Factor the group order
        self.factors = factor(self.group_order)

        self.stats = {
            'total_iterations': 0,
            'subgroup_solves': 0,
            'point_operations': 0,
            'found': False,
            'attack_type': 'pohlig_hellman',
            'group_order': self.group_order,
            'factorization': self.factors,
            'time_elapsed': 0
        }

    def print_stats(self):
        """Print algorithm statistics."""
        print("\n" + "=" * 70)
        print("POHLIG-HELLMAN STATISTICS")
        print("=" * 70)
        print(f"Attack Type:            {self.stats['attack_type']}")
        print(f"Group Order N:          {self.group_order}")
        print(f"Factorization:          {' * '.join(f'{p}^{e}' for p, e in self.factors)}")
        print(f"Subgroup Solves:        {self.stats['subgroup_solves']}")
        print(f"Total Iterations:       {self.stats['total_iterations']}")
        print(f"Point Operations:       {self.stats['point_operations']}")
        print(f"Time Elapsed:           {self.stats['time_elapsed']:.6f} seconds")
        print(f"Private Key Found:      {'Yes' if self.stats['found'] else 'No'}")
        print("=" * 70)

    def run(self):
        """
        Execute Pohlig-Hellman algorithm.

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

        result = self._pohlig_hellman(target_point)

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
                Q = scalar_multiply(result, self.generator)
                print(f"Verify: {to_hex(result)} * G = {point_to_hex(Q)}")
                print(f"Match:  {Q == self.target}")

        return self.result

    def _print_header(self):
        """Print algorithm header."""
        print(f'\n{"=" * 70}')
        print("POHLIG-HELLMAN ALGORITHM")
        print(f'{"=" * 70}')
        print()
        print(f'Target Q:       {point_to_hex(self.target)}')
        print(f'Group order N:  {self.group_order}')
        print(f'Factorization:  {" * ".join(f"{p}^{e}" for p, e in self.factors)}')
        print()

        if len(self.factors) == 1 and self.factors[0][1] == 1:
            print("WARNING: N is prime! Pohlig-Hellman provides no speedup.")
            print("         Falling back to baby-step giant-step.")
        else:
            # Calculate expected work
            work = sum(e * (math.sqrt(p) + math.log2(p)) for p, e in self.factors)
            naive_work = math.sqrt(self.group_order)
            print(f'Expected work:  ~{work:.1f} operations')
            print(f'Naive BSGS:     ~{naive_work:.1f} operations')
            print(f'Speedup:        ~{naive_work/work:.1f}x')

    def _pohlig_hellman(self, target_point):
        """
        Main Pohlig-Hellman algorithm.

        For each prime power p^e dividing N:
        1. Compute d mod p^e by solving in the subgroup of order p^e
        2. Combine all partial results using CRT
        """
        if self.verbose:
            print(f'\n{"=" * 70}')
            print("SOLVING DISCRETE LOG BY PRIME POWER SUBGROUPS")
            print(f'{"=" * 70}')

        partial_dlogs = []  # d mod p^e for each factor
        moduli = []          # p^e values

        for p, e in self.factors:
            prime_power = p ** e

            if self.verbose:
                print(f'\n{"="*50}')
                print(f'Solving d mod {p}^{e} = {prime_power}')
                print(f'{"="*50}')

            # Solve d mod p^e
            d_mod_pe = self._solve_prime_power(target_point, p, e)

            if d_mod_pe is None:
                if self.verbose:
                    print(f'  Failed to solve mod {prime_power}')
                return None

            if self.verbose:
                print(f'  Result: d = {d_mod_pe} (mod {prime_power})')

            partial_dlogs.append(d_mod_pe)
            moduli.append(prime_power)
            self.stats['subgroup_solves'] += 1

        # Combine using CRT
        if self.verbose:
            print(f'\n{"=" * 70}')
            print("COMBINING WITH CHINESE REMAINDER THEOREM")
            print(f'{"=" * 70}')
            for d_i, m_i in zip(partial_dlogs, moduli):
                print(f'  d = {d_i} (mod {m_i})')

        d = chinese_remainder_theorem(partial_dlogs, moduli)

        if self.verbose:
            print(f'\n  CRT result: d = {d} (mod {self.group_order})')

        # Handle d = 0 case
        if d == 0:
            d = self.group_order

        # Verify
        if scalar_multiply(d, self.generator) == target_point:
            self.stats['found'] = True
            return d

        return None

    def _solve_prime_power(self, Q, p: int, e: int) -> Optional[int]:
        """
        Solve d mod p^e using the prime power subgroup.

        Uses the "lifting" technique:
        1. Solve d0 mod p (in subgroup of order p)
        2. Solve d1 mod p (to get d mod p^2)
        3. Continue until d mod p^e

        d = d0 + d1*p + d2*p^2 + ... + d_{e-1}*p^{e-1}
        """
        n_div_pe = self.group_order // (p ** e)

        # Compute generator and target in subgroup of order p^e
        # h = G^(N/p^e) has order p^e
        h = scalar_multiply(n_div_pe, self.generator)
        # Q' = Q^(N/p^e)
        Q_prime = scalar_multiply(n_div_pe, Q)

        if self.verbose:
            print(f'\n  Subgroup generator h = {n_div_pe}*G = {point_to_hex(h)}')
            print(f"  Subgroup target Q' = {n_div_pe}*Q = {point_to_hex(Q_prime)}")

        # For prime order subgroup, use BSGS
        # For prime powers, use Pohlig lifting

        if e == 1:
            # Simple case: solve in subgroup of prime order p
            return self._bsgs_subgroup(Q_prime, h, p)
        else:
            # Prime power case: use lifting
            return self._solve_prime_power_lifting(Q_prime, h, p, e)

    def _solve_prime_power_lifting(self, Q, h, p: int, e: int) -> Optional[int]:
        """
        Solve DLP in subgroup of prime power order p^e using Pohlig lifting.

        Finds d = d0 + d1*p + d2*p^2 + ... where each d_i in [0, p-1]
        """
        if self.verbose:
            print(f'\n  Using Pohlig lifting for p^e = {p}^{e}')

        # gamma = h^(p^(e-1)) has order p
        gamma = scalar_multiply(p ** (e - 1), h)

        if self.verbose:
            print(f'  gamma = h^{p**(e-1)} = {point_to_hex(gamma)} (order {p})')

        d = 0
        h_neg_d = Q  # Will hold Q * h^(-d) as we accumulate

        for k in range(e):
            if self.verbose:
                print(f'\n  --- Lifting step k={k} ---')

            # Compute (Q * h^(-d))^(p^(e-1-k))
            exp = p ** (e - 1 - k)
            point_k = scalar_multiply(exp, h_neg_d)

            if self.verbose:
                print(f'  point_k = (Q * h^(-{d}))^{exp} = {point_to_hex(point_k)}')

            # Solve point_k = gamma^(d_k) for d_k in [0, p-1]
            d_k = self._bsgs_subgroup(point_k, gamma, p)

            if d_k is None:
                return None

            if self.verbose:
                print(f'  d_{k} = {d_k}')

            # Update d
            d += d_k * (p ** k)

            # Update h_neg_d = Q * h^(-d)
            h_neg_d = point_add(Q, point_negate(scalar_multiply(d, h)))

            if self.verbose:
                print(f'  d so far: {d}')

        return d

    def _bsgs_subgroup(self, Q, h, order: int) -> Optional[int]:
        """
        Baby-step Giant-step for subgroup of given order.

        Solves: Q = d * h where d in [0, order-1]
        """
        self.stats['total_iterations'] += 1

        if Q is None or Q == INFINITY:
            # Q = O means d = 0 (or multiple of order)
            return 0

        if h is None or h == INFINITY:
            # Can't solve with trivial generator
            return 0 if (Q is None or Q == INFINITY) else None

        m = math.ceil(math.sqrt(order))

        if self.verbose:
            print(f'  BSGS in subgroup of order {order}, m = {m}')

        # Baby steps: build table of j*h for j = 0 to m-1
        baby_table = {}
        point = INFINITY
        for j in range(m):
            self.stats['point_operations'] += 1
            if point is None:
                baby_table['infinity'] = j
            else:
                baby_table[point] = j
            point = point_add(point, h)

        # Giant steps: compute Q - i*m*h
        mh = scalar_multiply(m, h)
        neg_mh = point_negate(mh) if mh else None

        gamma = Q
        for i in range(m):
            self.stats['point_operations'] += 1
            self.stats['total_iterations'] += 1

            # Check for match
            if gamma is None and 'infinity' in baby_table:
                j = baby_table['infinity']
                return (i * m + j) % order
            if gamma is not None and gamma in baby_table:
                j = baby_table[gamma]
                return (i * m + j) % order

            gamma = point_add(gamma, neg_mh)

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


def point_negate(point):
    """Negate a point: -P = (x, -y)."""
    if point is None or point == INFINITY:
        return INFINITY
    return (point[0], (-point[1]) % P)


def demo_smooth_order():
    """
    Demonstrate Pohlig-Hellman on a curve with SMOOTH order.

    We'll create a toy example where order factors nicely.
    """
    print("\n" + "=" * 70)
    print("POHLIG-HELLMAN WITH SMOOTH ORDER (TOY EXAMPLE)")
    print("=" * 70)

    # For demonstration, pretend we have a group of order 12 = 4 * 3
    # We'll simulate this by working modulo 12 conceptually

    print("""
EXAMPLE: Group order N = 12 = 2^2 * 3

To find d where Q = d*G:

1. Solve d mod 4:
   - Move to subgroup of order 4
   - Only 4 possibilities: try 0, 1, 2, 3
   - Say we find d = 3 (mod 4)

2. Solve d mod 3:
   - Move to subgroup of order 3
   - Only 3 possibilities: try 0, 1, 2
   - Say we find d = 2 (mod 3)

3. Chinese Remainder Theorem:
   - d = 3 (mod 4)
   - d = 2 (mod 3)
   - Solution: d = 11 (mod 12)

Work done: 4 + 3 = 7 operations
Brute force: 12 operations
BSGS: sqrt(12) ~ 3.5 operations

For large smooth N, the savings are ENORMOUS:
- N = 2^32:  Brute = 2^32, BSGS = 2^16, PH = 32*2 = 64 !!!
""")


def demo():
    """Demonstrate Pohlig-Hellman algorithm."""
    print("\n" + "=" * 70)
    print("POHLIG-HELLMAN ALGORITHM DEMONSTRATION")
    print("=" * 70)

    # Show factorization of our curve's order
    print(f"\nYour 4-bit curve:")
    print(f"  Group order N = {N}")
    print(f"  Factorization: {factor(N)}")

    if len(factor(N)) == 1 and factor(N)[0][1] == 1:
        print(f"\n  N = {N} is PRIME!")
        print("  Pohlig-Hellman provides NO speedup for prime order.")
        print("  This is actually good for security - your curve resists PH attack.")

    # Create a keypair
    private_key = 0x0B  # 11 decimal
    public_key = scalar_multiply(private_key, G)

    print(f"\nTest keypair:")
    print(f"  Private key (SECRET): d = {to_hex(private_key)} ({private_key} decimal)")
    print(f"  Public key (PUBLIC):  Q = {point_to_hex(public_key)}")

    print("\n" + "-" * 70)
    print("Running Pohlig-Hellman (will fallback to BSGS for prime N)...")
    print("-" * 70)

    mechanism = PohligHellmanECDSA4bitMechanism(public_key, verbose=True)
    result = mechanism.run()

    if result['found']:
        print(f"\nSUCCESS: Found d = {to_hex(result['private_key'])}")

    # Show the smooth order example
    demo_smooth_order()

    print("\n" + "=" * 70)
    print("SECURITY IMPLICATIONS")
    print("=" * 70)
    print("""
WHY CURVE DESIGNERS CHOOSE PRIME ORDER:

1. Bitcoin's secp256k1:
   - N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
   - This is PRIME (verified)
   - Pohlig-Hellman is useless against it

2. Vulnerable curves (historical):
   - Some old/weak curves had smooth-order subgroups
   - Pohlig-Hellman could break them efficiently
   - Modern curves avoid this by design

3. Embedding degree attacks:
   - Related to Pohlig-Hellman on pairing-friendly curves
   - Certain curves weak against MOV/Frey-Ruck attacks

BOTTOM LINE:
- Your 4-bit curve with N=19 (prime) is resistant to Pohlig-Hellman
- Bitcoin's curve with prime N is also resistant
- The algorithm is educational for understanding why prime order matters
""")


if __name__ == "__main__":
    demo()
