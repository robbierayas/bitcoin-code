"""
Rollback Point Multiply (Scalar Multiplication) - 4-bit ECDSA

This module attempts to reverse scalar multiplication Q = d * G
by recursively decomposing point additions back to the generator G.

Uses the recursive candidate filtering pattern:
- valid_candidates: list of candidate paths being explored
- step_candidates: all (P1, P2) pairs to try at each step
- recurse: filters candidates depth by depth until G is found

Educational demonstration of ECDLP rollback complexity.
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

# Precomputed addend values: ADDENDS[i] = 2^i * G
# Used in double-and-add: addend starts at G, doubles each bit
# Cycles after 18 since 2^18 ≡ 1 (mod N=19)
ADDENDS = [
    (0x05, 0x01),  # 2^0  * G = G
    (0x06, 0x03),  # 2^1  * G = 2G
    (0x03, 0x01),  # 2^2  * G = 4G
    (0x0D, 0x07),  # 2^3  * G = 8G
    (0x0A, 0x0B),  # 2^4  * G = 16G
    (0x10, 0x04),  # 2^5  * G
    (0x00, 0x06),  # 2^6  * G
    (0x09, 0x01),  # 2^7  * G
    (0x07, 0x06),  # 2^8  * G
    (0x05, 0x10),  # 2^9  * G
    (0x06, 0x0E),  # 2^10 * G
    (0x03, 0x10),  # 2^11 * G
    (0x0D, 0x0A),  # 2^12 * G
    (0x0A, 0x06),  # 2^13 * G
    (0x10, 0x0D),  # 2^14 * G
    (0x00, 0x0B),  # 2^15 * G
    (0x09, 0x10),  # 2^16 * G
    (0x07, 0x0B),  # 2^17 * G
]

# Reverse lookup: point -> bit position (if point is 2^i * G)
ADDEND_TO_BIT = {pt: i for i, pt in enumerate(ADDENDS)}


def get_addend(bit_pos):
    """Get precomputed addend for bit position: 2^bit_pos * G."""
    if bit_pos < len(ADDENDS):
        return ADDENDS[bit_pos]
    # For larger bit positions, cycle (2^18 ≡ 1 mod N=19)
    return ADDENDS[bit_pos % 18]


def is_addend(pt):
    """Check if point is a precomputed addend. Returns bit position or None."""
    return ADDEND_TO_BIT.get(pt)


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


def get_step_candidates(target_point, require_addend=False):
    """
    Get all (P1, P2) pairs such that P1 + P2 = target_point.
    Skips infinity. Returns list of (p1, p2, slope, is_doubling, addend_info).

    CONSTRAINT: In real scalar multiply (double-and-add), one operand is always
    an addend value (2^i * G). Set require_addend=True to filter by this.

    addend_info is (bit_pos_p1, bit_pos_p2) where bit_pos is None if not an addend.
    """
    if target_point is None:
        return []

    all_points = get_all_curve_points()
    results = []

    for p1 in all_points:
        for p2 in all_points:
            result = point_add(p1, p2)
            if result == target_point:
                # Check if either point is an addend (2^i * G)
                add_bit_p1 = is_addend(p1)
                add_bit_p2 = is_addend(p2)

                # Filter: in scalar multiply, one operand is always an addend
                if require_addend and add_bit_p1 is None and add_bit_p2 is None:
                    continue

                slope, is_doubling = compute_slope(p1, p2)
                results.append((p1, p2, slope, is_doubling, (add_bit_p1, add_bit_p2)))

    return results


def extend_candidate(cand, p1, p2, slope, is_doubling, depth):
    """
    Extend a candidate with a new rollback step.
    Returns new candidate dict.
    """
    new_steps = cand.get('steps', {}).copy()
    new_steps[depth] = {
        'current': cand['current'],
        'p1': p1,
        'p2': p2,
        'slope': slope,
        'is_doubling': is_doubling
    }

    return {
        'path': cand['path'] + [(p1, p2, slope, is_doubling)],
        'current': p1,  # Follow p1 as the chain
        'steps': new_steps
    }


def check_found_generator(cand):
    """Check if candidate's current point is the generator G."""
    return cand['current'] == G


def rollback_multiply(start_point, max_depth=3, max_candidates=None):
    """
    Recursively rollback scalar multiplication from start_point toward G.

    Uses the candidate filtering pattern:
    1. Start with initial candidate at start_point
    2. At each depth, get step_candidates (all P1+P2=current pairs)
    3. Extend valid_candidates with each possibility
    4. Stop when max_depth reached or max_candidates hit

    Args:
        start_point: Point to start rollback from (Q = d*G)
        max_depth: Maximum recursion depth (default 3)
        max_candidates: Maximum candidates to track (default: estimated from curve)

    Returns dict with results and metadata.
    """
    # Estimate max_candidates from curve parameters if not provided
    num_points = len(get_all_curve_points())
    pairs_per_point = num_points
    branching_factor = pairs_per_point * 2  # Follow both p1 and p2
    if max_candidates is None:
        max_candidates = branching_factor ** max_depth

    print(f"\n  Starting scalar multiply rollback from {point_to_hex(start_point)}")
    print(f"  Target: find path back to G = {point_to_hex(G)}")
    print(f"  Curve has {num_points} points, ~{pairs_per_point} pairs per point")
    print(f"  Limits: max_depth={max_depth}, max_candidates={max_candidates}")

    # Initialize with single candidate at start_point
    valid_candidates = [{
        'path': [],
        'current': start_point,
        'steps': {0: {'current': start_point, 'p1': None, 'p2': None, 'slope': None, 'is_doubling': None}}
    }]

    found_G = []  # Candidates that reached G
    step_log = []  # Track candidates at each depth

    def recurse(depth, candidates):
        """Recursively filter candidates."""
        nonlocal found_G

        # Check limits
        if depth > max_depth:
            return candidates
        if not candidates:
            return []

        print(f"\n  Depth {depth}: {len(candidates)} candidates")

        # Check if any candidates have reached G
        found_at_depth = 0
        for cand in candidates:
            if check_found_generator(cand):
                found_G.append(cand)
                found_at_depth += 1
        if found_at_depth > 0:
            print(f"    FOUND G: {found_at_depth} paths at this depth")

        # Get step candidates for each current point
        next_candidates = []

        for cand in candidates:
            if len(next_candidates) >= max_candidates:
                break

            current = cand['current']

            # Skip if already at G
            if current == G:
                continue

            # Get all (P1, P2) pairs for this point
            step_cands = get_step_candidates(current)

            # Show sample
            if len(next_candidates) < 3:
                print(f"    Current={point_to_hex(current)}: {len(step_cands)} pairs")

            # Extend candidate with each possibility
            for p1, p2, slope, is_doubling, addend_info in step_cands:
                if len(next_candidates) >= max_candidates:
                    break

                new_cand = extend_candidate(cand, p1, p2, slope, is_doubling, depth)
                new_cand['addend_info'] = addend_info
                next_candidates.append(new_cand)

                # Also try following p2 as the chain (branching)
                new_cand_p2 = {
                    'path': cand['path'] + [(p1, p2, slope, is_doubling)],
                    'current': p2,
                    'steps': new_cand['steps'].copy(),
                    'addend_info': addend_info
                }
                next_candidates.append(new_cand_p2)

        step_log.append((depth, len(candidates), len(next_candidates)))
        if len(next_candidates) >= max_candidates:
            print(f"    -> {len(next_candidates)} candidates (hit max_candidates)")
        else:
            print(f"    -> {len(next_candidates)} new candidates")

        # Recurse
        return recurse(depth + 1, next_candidates)

    # Run recursion
    final_candidates = recurse(1, valid_candidates)

    return {
        'found_G': found_G,
        'final_candidates': final_candidates,
        'step_log': step_log,
        'start_point': start_point
    }


def demo():
    """Run demo with scalar multiply rollback."""
    print("=" * 70)
    print("SCALAR MULTIPLY ROLLBACK - 4-BIT ECDSA")
    print("=" * 70)

    # Generate keypair
    d = 0x07  # Private key
    private_key, public_key = generate_keypair(d)

    print(f"\nPrivate key: {to_hex(private_key)}")
    print(f"Public key:  {point_to_hex(public_key)}")
    print(f"Generator:   {point_to_hex(G)}")

    # Show forward computation
    print(f"\n--- FORWARD: Computing Q = {to_hex(d)} * G ---")
    print(f"d = {to_hex(d)} = {bin(d)[2:].zfill(4)} binary")

    result = INFINITY
    addend = G
    step = 0
    k = d

    headers = ["Step", "Bit", "Operation", "Result", "Slope"]
    rows = []

    while k:
        bit = k & 1
        if bit:
            old_result = result
            result = point_add(result, addend)
            slope, _ = compute_slope(old_result, addend)
            slope_str = to_hex(slope) if slope is not None else "-"
            rows.append([step, bit, "result += addend", point_to_hex(result), slope_str])

        old_addend = addend
        addend = point_add(addend, addend)
        slope, _ = compute_slope(old_addend, old_addend)
        slope_str = to_hex(slope) if slope is not None else "-"
        rows.append([step, "-", "addend = 2*addend", point_to_hex(addend), slope_str])

        k >>= 1
        step += 1

    print_table(headers, rows, None)
    print(f"\nFinal Q = {point_to_hex(result)}")

    # Show addend constraint effect
    print("\n" + "=" * 70)
    print("ADDEND CONSTRAINT")
    print("=" * 70)
    print("\nIn double-and-add, one operand is always 2^i * G (an addend).")
    print("This filters invalid pairs during rollback.\n")

    all_pairs = get_step_candidates(public_key, require_addend=False)
    addend_pairs = get_step_candidates(public_key, require_addend=True)

    print(f"Q = {point_to_hex(public_key)}")
    print(f"  All pairs where P1 + P2 = Q:     {len(all_pairs)}")
    print(f"  Pairs with addend (2^i * G):     {len(addend_pairs)}")
    print(f"  Reduction:                       {len(all_pairs) - len(addend_pairs)} pairs filtered")

    print("\nPairs containing an addend:")
    headers = ["#", "P1", "2^i?", "P2", "2^i?", "Slope"]
    rows = []
    for i, (p1, p2, slope, is_dbl, (ab1, ab2)) in enumerate(addend_pairs):
        rows.append([
            i + 1,
            point_to_hex(p1),
            f"2^{ab1}" if ab1 is not None else "-",
            point_to_hex(p2),
            f"2^{ab2}" if ab2 is not None else "-",
            to_hex(slope) if slope else "-"
        ])
    print_table(headers, rows, None)

    # Now rollback
    print("\n" + "=" * 70)
    print("ROLLBACK: Tracing from Q back to G")
    print("=" * 70)

    results = rollback_multiply(public_key, max_depth=3)

    # Show results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\nPaths that reached G: {len(results['found_G'])}")

    # Analyze paths that found G at depth 1 (direct decomposition of Q)
    depth1_paths = [c for c in results['found_G'] if len(c['path']) == 1]

    if depth1_paths:
        print(f"\n--- DEPTH 1 PATHS (Direct G + P = Q) ---")
        print("If G + P = Q and P = k*G, then d = (1 + k) mod N")
        print()

        headers = ["#", "P1", "P2", "Other Point", "k (other=k*G)", "d = 1+k", "d*G = Q?"]
        rows = []

        recovered_keys = set()
        for i, cand in enumerate(depth1_paths):
            p1, p2, slope, is_double = cand['path'][0]

            if p1 == G:
                other = p2
            else:
                other = p1

            k = point_to_scalar(other)
            if k is not None:
                d_candidate = (1 + k) % N
                check = point_multiply(d_candidate, G)
                valid = (check == public_key)
                recovered_keys.add(d_candidate)

                rows.append([
                    i + 1,
                    point_to_hex(p1),
                    point_to_hex(p2),
                    point_to_hex(other),
                    to_hex(k),
                    to_hex(d_candidate),
                    "YES" if valid else "NO"
                ])

        print_table(headers, rows, None)

        # Verify recovered keys
        print(f"\n--- VERIFICATION ---")
        print(f"Actual private key: {to_hex(private_key)}")
        print(f"Recovered key candidates: {[to_hex(k) for k in sorted(recovered_keys)]}")

        for d_test in sorted(recovered_keys):
            test_Q = point_multiply(d_test, G)
            match = (test_Q == public_key)
            print(f"  d={to_hex(d_test)}: d*G = {point_to_hex(test_Q)} {'== Q (VALID KEY!)' if match else '!= Q'}")

        # Sign and verify with recovered key
        valid_keys = [k for k in recovered_keys if point_multiply(k, G) == public_key]
        if valid_keys:
            d_recovered = valid_keys[0]
            msg_hash = 0x0B
            print(f"\n--- SIGN/VERIFY TEST with recovered key d={to_hex(d_recovered)} ---")
            r, s = sign(d_recovered, msg_hash, k=0x05)
            print(f"Message hash: {to_hex(msg_hash)}")
            print(f"Signature: r={to_hex(r)}, s={to_hex(s)}")
            is_valid = verify(public_key, msg_hash, (r, s))
            print(f"Verify with original public key: {is_valid}")

    # Show longest depth paths if > 1
    if results['found_G']:
        max_len = max(len(c['path']) for c in results['found_G'])
        if max_len > 1:
            longest_paths = [c for c in results['found_G'] if len(c['path']) == max_len]
            print(f"\n--- LONGEST DEPTH PATHS (depth {max_len}) ---")
            print(f"Found {len(longest_paths)} paths at depth {max_len}")
            print()

            for i, cand in enumerate(longest_paths[:5]):
                print(f"Path {i+1}:")
                headers = ["Step", "P1", "k1", "P2", "k2", "Slope", "G?"]
                rows = []
                for j, (p1, p2, slope, is_double) in enumerate(cand['path']):
                    k1 = point_to_scalar(p1)
                    k2 = point_to_scalar(p2)
                    has_g = "P1" if p1 == G else ("P2" if p2 == G else "")
                    rows.append([
                        j + 1,
                        point_to_hex(p1),
                        to_hex(k1) if k1 else "-",
                        point_to_hex(p2),
                        to_hex(k2) if k2 else "-",
                        to_hex(slope) if slope else "-",
                        has_g
                    ])
                print_table(headers, rows, None)
                print()

    # Step log
    if results['step_log']:
        print("\n--- Candidate Growth ---")
        headers = ["Depth", "Input", "Output"]
        rows = [[d, i, o] for d, i, o in results['step_log']]
        print_table(headers, rows, None)

    # Key insight
    print("\n--- KEY INSIGHT ---")
    print("Scalar multiply rollback explores all possible decompositions of Q.")
    print("Each depth multiplies candidates by ~34 (17 pairs * 2 branches).")
    print("On a 256-bit curve, this branching makes brute-force impossible.")


if __name__ == "__main__":
    demo()
