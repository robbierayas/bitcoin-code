"""
Rollback Point Addition - 4-bit ECDSA

This module reverses a SINGLE point addition operation.
Given a point Q, find all (P1, P2) pairs such that P1 + P2 = Q.

This is strictly depth 1 - no recursion.
For recursive scalar multiply rollback, see rollbackPointMultiply4bit.py.

Educational demonstration of point addition ambiguity.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.ecdsa4bit import (
    generate_keypair, point_multiply, point_add,
    point_to_hex, to_hex, G, p, A, B, N, INFINITY, mod_inverse, sign, verify
)
from cryptography.bitUtils import print_table


# Cache all curve points (computed once)
ALL_CURVE_POINTS = None
POINT_TO_SCALAR = None  # Lookup: point -> k where point = k*G


def get_all_curve_points():
    """Get all points on the 4-bit curve (cached)."""
    global ALL_CURVE_POINTS
    if ALL_CURVE_POINTS is None:
        points = []
        for x in range(p):
            y_squared = (x * x * x + A * x + B) % p
            for y in range(p):
                if (y * y) % p == y_squared:
                    points.append((x, y))
        ALL_CURVE_POINTS = points
    return ALL_CURVE_POINTS


def get_point_to_scalar():
    """Build lookup table: point -> scalar k where point = k*G."""
    global POINT_TO_SCALAR
    if POINT_TO_SCALAR is None:
        POINT_TO_SCALAR = {}
        for k in range(1, N):
            pt = point_multiply(k, G)
            if pt is not None:
                POINT_TO_SCALAR[pt] = k
    return POINT_TO_SCALAR


def point_to_scalar(pt):
    """Get scalar k where pt = k*G, or None if not found."""
    lookup = get_point_to_scalar()
    return lookup.get(pt)


def compute_slope(p1, p2):
    """
    Compute the slope used in point addition.
    Returns (slope, is_doubling) or (None, None) if undefined.
    """
    if p1 is None or p2 is None:
        return None, None

    x1, y1 = p1
    x2, y2 = p2

    # Check if result would be infinity
    if x1 == x2 and (y1 + y2) % p == 0:
        return None, None

    if x1 == x2 and y1 == y2:
        # Point doubling: slope = (3x^2 + a) / (2y)
        if y1 == 0:
            return None, None
        numerator = (3 * x1 * x1 + A) % p
        denominator = (2 * y1) % p
        is_doubling = True
    else:
        # Point addition: slope = (y2 - y1) / (x2 - x1)
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
        is_doubling = False

    slope = (numerator * mod_inverse(denominator, p)) % p
    return slope, is_doubling


def rollback_point_add(target_point):
    """
    Find all (P1, P2) pairs such that P1 + P2 = target_point.

    This is a single-step rollback (depth 1 only).
    Skips pairs involving infinity.

    Returns list of dicts with: p1, p2, slope, is_doubling, k1, k2
    """
    if target_point is None:
        return []

    all_points = get_all_curve_points()
    results = []

    for p1 in all_points:
        for p2 in all_points:
            result = point_add(p1, p2)
            if result == target_point:
                slope, is_doubling = compute_slope(p1, p2)
                k1 = point_to_scalar(p1)
                k2 = point_to_scalar(p2)
                results.append({
                    'p1': p1,
                    'p2': p2,
                    'slope': slope,
                    'is_doubling': is_doubling,
                    'k1': k1,
                    'k2': k2,
                    'has_G': p1 == G or p2 == G
                })

    return results


def demo():
    """Demonstrate single point addition rollback."""
    print("=" * 70)
    print("POINT ADDITION ROLLBACK - 4-BIT ECDSA (DEPTH 1 ONLY)")
    print("=" * 70)

    # Generate keypair
    d = 0x07  # Private key
    private_key, public_key = generate_keypair(d)

    print(f"\nPrivate key: {to_hex(private_key)}")
    print(f"Public key Q: {point_to_hex(public_key)}")
    print(f"Generator G:  {point_to_hex(G)}")

    # Rollback Q
    print(f"\n--- ROLLBACK: Find all (P1, P2) where P1 + P2 = Q ---")

    pairs = rollback_point_add(public_key)
    print(f"Found {len(pairs)} pairs")

    # Display table
    headers = ["#", "P1", "k1", "P2", "k2", "Slope", "Type", "Has G?"]
    rows = []
    for i, pair in enumerate(pairs):
        rows.append([
            i + 1,
            point_to_hex(pair['p1']),
            to_hex(pair['k1']) if pair['k1'] else "-",
            point_to_hex(pair['p2']),
            to_hex(pair['k2']) if pair['k2'] else "-",
            to_hex(pair['slope']) if pair['slope'] else "-",
            "dbl" if pair['is_doubling'] else "add",
            "YES" if pair['has_G'] else ""
        ])
    print_table(headers, rows, None)

    # Analyze pairs with G
    pairs_with_G = [p for p in pairs if p['has_G']]
    print(f"\n--- PAIRS CONTAINING G ({len(pairs_with_G)} found) ---")
    print("If G + P = Q and P = k*G, then Q = (1+k)*G, so d = 1 + k")
    print()

    recovered_keys = set()
    for pair in pairs_with_G:
        if pair['p1'] == G:
            other = pair['p2']
            k_other = pair['k2']
        else:
            other = pair['p1']
            k_other = pair['k1']

        if k_other is not None:
            d_candidate = (1 + k_other) % N
            check = point_multiply(d_candidate, G)
            valid = (check == public_key)
            recovered_keys.add(d_candidate)
            status = "VALID" if valid else "invalid"
            print(f"  G + {point_to_hex(other)} (k={to_hex(k_other)}) -> d = 1 + {k_other} = {d_candidate} ({to_hex(d_candidate)}) [{status}]")

    # Verification
    print(f"\n--- VERIFICATION ---")
    print(f"Actual private key: {to_hex(private_key)}")
    print(f"Recovered candidates: {[to_hex(k) for k in sorted(recovered_keys)]}")

    valid_keys = [k for k in recovered_keys if point_multiply(k, G) == public_key]
    if valid_keys:
        d_recovered = valid_keys[0]
        print(f"\nValid key found: d = {to_hex(d_recovered)}")

        # Sign and verify
        msg_hash = 0x0B
        r, s = sign(d_recovered, msg_hash, k=0x05)
        is_valid = verify(public_key, msg_hash, (r, s))
        print(f"\nSign/Verify test:")
        print(f"  Message hash: {to_hex(msg_hash)}")
        print(f"  Signature: r={to_hex(r)}, s={to_hex(s)}")
        print(f"  Verify: {is_valid}")

    # Key insight
    print("\n--- KEY INSIGHT ---")
    print(f"Given Q, there are {len(pairs)} possible (P1, P2) decompositions.")
    print(f"Only {len(pairs_with_G)} contain G, revealing the private key relationship.")
    print("On larger curves, P(G in random pair) -> 0, making this useless.")


def demo_known_addition():
    """Demo with a known point addition."""
    print("\n" + "=" * 70)
    print("KNOWN POINT ADDITION ROLLBACK")
    print("=" * 70)

    # Compute 2*G + 3*G = 5*G
    p1 = point_multiply(2, G)  # 2*G
    p2 = point_multiply(3, G)  # 3*G
    target = point_add(p1, p2)  # 5*G

    print(f"\nForward: {point_to_hex(p1)} (2*G) + {point_to_hex(p2)} (3*G) = {point_to_hex(target)} (5*G)")

    slope, is_dbl = compute_slope(p1, p2)
    print(f"Slope used: {to_hex(slope)}")

    # Rollback
    print(f"\nRollback: Find all (P1, P2) where P1 + P2 = 5*G")
    pairs = rollback_point_add(target)

    headers = ["#", "P1", "k1", "P2", "k2", "k1+k2", "Slope"]
    rows = []
    for i, pair in enumerate(pairs):
        k1 = pair['k1']
        k2 = pair['k2']
        k_sum = (k1 + k2) % N if k1 and k2 else None
        rows.append([
            i + 1,
            point_to_hex(pair['p1']),
            to_hex(k1) if k1 else "-",
            point_to_hex(pair['p2']),
            to_hex(k2) if k2 else "-",
            to_hex(k_sum) if k_sum else "-",
            to_hex(pair['slope']) if pair['slope'] else "-"
        ])
    print_table(headers, rows, None)

    # Find original pair
    print(f"\nOriginal pair (2*G + 3*G):")
    for pair in pairs:
        if (pair['p1'] == p1 and pair['p2'] == p2) or (pair['p1'] == p2 and pair['p2'] == p1):
            print(f"  Found: P1={point_to_hex(pair['p1'])}, P2={point_to_hex(pair['p2'])}")
            print(f"  k1={pair['k1']}, k2={pair['k2']}, k1+k2={(pair['k1']+pair['k2']) % N}")

    print(f"\nBut we cannot distinguish which of {len(pairs)} pairs was actually used!")


if __name__ == "__main__":
    demo()
    demo_known_addition()
