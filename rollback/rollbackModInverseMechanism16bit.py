"""
Mod inverse step rollback mechanism - 16-bit test.

This module implements rollback for the Extended Euclidean Algorithm (EEA)
used in mod_inverse. The key insight is that integer division destroys
bit relationships, but rollback is possible if quotients are recorded.

The mechanism operates on mod_inverse_step, not the full mod_inverse function.

16-bit version uses ~16-bit prime and value for testing at larger scale.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Optional, Dict
from cryptography.bitUtils import ModInverseState, mod_inverse_full, print_table


# 16-bit test parameters
# p = 65521 is the largest 16-bit prime
# a = 48271 is a 16-bit value coprime to p
TEST_A_16BIT = 48271
TEST_P_16BIT = 65521


def mod_inverse_step_reverse(state: ModInverseState, quotient: int) -> ModInverseState:
    """
    Reverse ONE step of EEA given the quotient.

    Forward: (old_r, r) -> (r, old_r - q*r)
    Reverse: prev_old_r = r + q * old_r, prev_r = old_r
    """
    return ModInverseState(
        old_r=state.r + quotient * state.old_r,
        r=state.old_r,
        old_s=state.s + quotient * state.old_s,
        s=state.old_s,
        step=state.step - 1,
        quotients=state.quotients.copy()
    )


def rollback_with_quotients(state: ModInverseState, n_steps: int) -> ModInverseState:
    """Roll back n steps using state's quotients."""
    result = state.copy()
    for i in range(n_steps):
        q_idx = len(state.quotients) - 1 - i
        result = mod_inverse_step_reverse(result, state.quotients[q_idx])
    return result


def rollback_without_quotients(state: ModInverseState, known_p: int,
                                timeout_sec: float = 300.0,
                                max_q: int = 500,
                                max_candidates: int = 100000) -> ModInverseState:
    """
    Attempt rollback WITHOUT quotients (brute force).

    Makes a copy, clears quotients, tries to recover them via brute force.
    Returns state with recovered quotients and reconstructed_bits.

    Args:
        state: Final state from mod_inverse_full (quotients will be ignored)
        known_p: The modulus p (used to validate candidates)
        timeout_sec: Timeout in seconds (default 300 = 5 min for 16-bit)
        max_q: Maximum quotient value to try per step (increased for 16-bit)
        max_candidates: Maximum candidates to track

    Returns:
        ModInverseState with:
            - quotients: recovered quotient sequence (if found)
            - reconstructed_bits: {pos: bit} for bits determined across all candidates
    """
    start_time = time.time()
    num_steps = state.step

    # Work with a clean copy (no quotients)
    work_state = state.copy()
    work_state.quotients = []
    work_state.reconstructed_bits = {}

    # Separate arrays for each candidate component
    candidate_old_r = []
    candidate_r = []
    candidate_quotients = []

    # Track step candidates and results per depth
    step_candidates_log = []  # [(depth, num_candidates, valid_count)]

    # Each valid_candidate is: {qs: [], old_r, r, old_s, s, steps: {step: state}}
    # qs is ordered from last step (depth 9) to first (depth 0)
    # steps tracks the state at each rollback step for this candidate

    def compute_prev_state(curr, q):
        """Compute previous EEA state given current state and quotient q."""
        return {
            'old_r': curr['r'] + q * curr['old_r'],
            'r': curr['old_r'],
            'old_s': curr['s'] + q * curr['old_s'],
            's': curr['old_s']
        }

    def is_swap_step(prev, q):
        """Detect if this is the swap step (step 0) from values."""
        # Swap step has: old_s=1, s=0, q=0, and old_r < r (a < p)
        return prev['old_s'] == 1 and prev['s'] == 0 and q == 0

    def is_valid_eea_step(prev, curr, q, depth):
        """Check if rolling back with quotient q produces a valid EEA state."""
        # CONSTRAINT 1: old_r > r (remainders strictly decrease)
        # Exception: swap step (step 0) can have old_r < r when a < p
        if is_swap_step(prev, q):
            # Allow old_r < r for the swap step
            pass
        elif prev['old_r'] <= prev['r']:
            return False

        # CONSTRAINT 2: old_r cannot exceed p
        if prev['old_r'] > known_p:
            return False

        # CONSTRAINT 3: r values must be non-negative
        if prev['r'] < 0 or prev['old_r'] < 0:
            return False

        # CONSTRAINT 4: Verify quotient matches forward division
        if prev['r'] > 0:
            expected_q = prev['old_r'] // prev['r']
            if expected_q != q:
                return False
            expected_new_r = prev['old_r'] % prev['r']
            if expected_new_r != curr['r']:
                return False

        # CONSTRAINT 5: Sign alternation of s
        if prev['old_s'] != 0 and prev['s'] != 0:
            if (prev['old_s'] > 0) == (prev['s'] > 0):
                if depth > num_steps - 2:
                    return False

        return True

    def extend_candidate(cand, q, depth):
        """Try to extend a candidate with quotient q. Returns new candidate or None."""
        curr = {'old_r': cand['old_r'], 'r': cand['r'],
                'old_s': cand['old_s'], 's': cand['s']}
        prev = compute_prev_state(curr, q)

        if not is_valid_eea_step(prev, curr, q, depth):
            return None

        # Valid - create new candidate with qs appended and step recorded
        new_steps = cand.get('steps', {}).copy()
        new_steps[depth] = {
            'old_r': prev['old_r'],
            'r': prev['r'],
            'old_s': prev['old_s'],
            's': prev['s'],
            'q': q
        }

        return {
            'qs': cand['qs'] + [q],
            'old_r': prev['old_r'],
            'r': prev['r'],
            'old_s': prev['old_s'],
            's': prev['s'],
            'steps': new_steps
        }

    def filter_candidates_at_depth(candidates, depth):
        """Filter candidates by trying all q values, keeping only those with valid extensions."""
        step_candidates = list(range(0, max_q + 1))
        next_candidates = []

        for cand in candidates:
            extended = False
            for q in step_candidates:
                new_cand = extend_candidate(cand, q, depth)
                if new_cand is not None:
                    next_candidates.append(new_cand)
                    extended = True

            # if not extended:
            #     print(f"    Removed: qs={cand['qs']} state=({cand['old_r']}, {cand['r']}, {cand['old_s']}, {cand['s']})")

        return next_candidates

    def check_initial_conditions(cand):
        """Check if candidate reached valid initial EEA state."""
        return cand['old_s'] == 1 and cand['s'] == 0 and cand['r'] == known_p

    # Known correct quotients (reversed: last step to first) from the actual state
    correct_qs = list(reversed(state.quotients))

    def check_correct_path_exists(candidates, steps_taken):
        """Verify correct quotient sequence is still among candidates."""
        expected_qs = correct_qs[:steps_taken]
        for cand in candidates:
            if cand['qs'] == expected_qs:
                return True
        return False

    def recurse(depth: int, valid_candidates: list = None, max_depth: int = 1):
        """Recursively filter candidates step by step."""
        # Check timeout
        if time.time() - start_time > timeout_sec:
            return []
        if len(candidate_old_r) >= max_candidates:
            return []

        # Initialize on first call
        if valid_candidates is None:
            initial_state = {
                'old_r': work_state.old_r,
                'r': work_state.r,
                'old_s': work_state.old_s,
                's': work_state.s
            }
            valid_candidates = [{
                'qs': [],
                'old_r': work_state.old_r,
                'r': work_state.r,
                'old_s': work_state.old_s,
                's': work_state.s,
                'steps': {num_steps: initial_state}  # Initial state at final step
            }]

        # Check depth limit
        steps_taken = num_steps - depth
        if steps_taken >= max_depth:
            for cand in valid_candidates:
                candidate_old_r.append(cand['old_r'])
                candidate_r.append(cand['r'])
                candidate_quotients.append(cand['qs'].copy())
            return valid_candidates

        # Check if reached initial state
        if depth == 0:
            final = [c for c in valid_candidates if check_initial_conditions(c)]
            for cand in final:
                candidate_old_r.append(cand['old_r'])
                candidate_r.append(cand['r'])
                candidate_quotients.append(cand['qs'].copy())
            return final

        # Filter candidates at this depth
        next_candidates = filter_candidates_at_depth(valid_candidates, depth)

        # Verify correct path still exists
        steps_taken = num_steps - depth + 1
        if not check_correct_path_exists(next_candidates, steps_taken):
            raise ValueError(f"Correct path lost at depth {depth}! Expected prefix: {correct_qs[:steps_taken]}")

        # Log
        step_candidates_log.append((depth, len(valid_candidates), len(next_candidates)))
        print(f"  Depth {depth}: {len(valid_candidates)} candidates -> {len(next_candidates)} valid")

        # Show sample candidates
        if next_candidates:
            for c in next_candidates[:3]:
                print(f"    qs={c['qs']} state=({c['old_r']}, {c['r']}, {c['old_s']}, {c['s']})")

        # Recurse
        return recurse(depth - 1, next_candidates, max_depth)

    # Trace the correct path manually first
    print(f"\n  TRACE: Checking correct quotient sequence in reverse...")
    trace_state = work_state.copy()
    for i, q in enumerate(correct_qs):
        prev_old_r = trace_state.r + q * trace_state.old_r
        prev_r = trace_state.old_r
        prev_old_s = trace_state.s + q * trace_state.old_s
        prev_s = trace_state.old_s
        print(f"    Step {i}: q={q} -> ({prev_old_r}, {prev_r}, {prev_old_s}, {prev_s})")

        # Check constraint 4
        if prev_r > 0:
            exp_q = prev_old_r // prev_r
            exp_r = prev_old_r % prev_r
            c4_pass = (exp_q == q and exp_r == trace_state.r)
            print(f"      C4: exp_q={exp_q}, exp_r={exp_r}, current_r={trace_state.r}, pass={c4_pass}")

        trace_state = ModInverseState(old_r=prev_old_r, r=prev_r, old_s=prev_old_s, s=prev_s, step=0)
    print()

    # Run brute force
    print(f"Starting rollback from step {num_steps}...")
    final_candidates = recurse(num_steps, None, max_depth=10)

    elapsed = time.time() - start_time
    timed_out = elapsed >= timeout_sec

    # Build result state
    result = state.copy()
    result.quotients = []
    result.reconstructed_bits = {}

    num_candidates = len(candidate_old_r)
    if num_candidates > 0:
        # If exactly one candidate, we found the quotients
        if num_candidates == 1:
            result.quotients = candidate_quotients[0]

        # Find bits consistent across ALL candidates
        max_bit = max(v.bit_length() for v in candidate_old_r)
        for pos in range(max_bit):
            bits = set((v >> pos) & 1 for v in candidate_old_r)
            if len(bits) == 1:
                result.reconstructed_bits[pos] = bits.pop()

    # Store metadata
    # Each candidate in final_candidates has 'steps' dict with state at each rollback step
    result._rollback_meta = {
        'num_candidates': num_candidates,
        'final_candidates': final_candidates,
        'candidate_old_r': candidate_old_r,
        'candidate_r': candidate_r,
        'candidate_quotients': candidate_quotients,
        'step_candidates_log': step_candidates_log,
        'elapsed_sec': elapsed,
        'timed_out': timed_out
    }

    return result


def verify_rollback(original: ModInverseState, recovered: ModInverseState,
                    a: int, p: int) -> Dict:
    """
    Verify recovered state against original.

    Returns dict with verification results.
    """
    # Expected initial values
    expected_old_r = a % p
    expected_r = p

    # If we recovered quotients, roll back and check
    if recovered.quotients:
        initial = rollback_with_quotients(recovered, len(recovered.quotients))
        quotients_match = (recovered.quotients == original.quotients)
        initial_match = (initial.old_r == expected_old_r and
                        initial.r == expected_r and
                        initial.old_s == 1 and initial.s == 0)
    else:
        quotients_match = False
        initial_match = False

    # Check reconstructed bits
    bits_correct = 0
    bits_wrong = 0
    for pos, bit in recovered.reconstructed_bits.items():
        actual = (expected_old_r >> pos) & 1
        if bit == actual:
            bits_correct += 1
        else:
            bits_wrong += 1

    return {
        'quotients_recovered': len(recovered.quotients) > 0,
        'quotients_match': quotients_match,
        'initial_match': initial_match,
        'bits_determined': len(recovered.reconstructed_bits),
        'bits_correct': bits_correct,
        'bits_wrong': bits_wrong,
        'meta': getattr(recovered, '_rollback_meta', {})
    }


def demo():
    """Demonstrate the mod_inverse step rollback mechanism with 16-bit values."""
    print("=" * 70)
    print("MOD_INVERSE STEP ROLLBACK MECHANISM - 16-BIT TEST")
    print("=" * 70)

    a, p = TEST_A_16BIT, TEST_P_16BIT
    print(f"\nTest parameters: a={a} ({a.bit_length()}-bit), p={p} ({p.bit_length()}-bit)")

    # =========================================================================
    # SECTION 1: Compute Inverse (populates state with quotients)
    # =========================================================================
    print("\n--- 1. COMPUTE INVERSE ---")

    state = mod_inverse_full(a, p)
    result = state.old_s % p

    print(f"mod_inverse({a}, {p}) = {result}")
    print(f"Verify: {a} * {result} mod {p} = {(a * result) % p}")
    print(f"Steps: {state.step}")
    print(f"Quotients: {state.quotients}")

    # =========================================================================
    # SECTION 2: Forward Execution Table
    # =========================================================================
    print("\n--- 2. FORWARD EXECUTION ---")

    headers = ["Step", "old_r", "r", "old_s", "s", "q"]
    rows = []
    for step in range(state.step + 1):
        s = rollback_with_quotients(state, state.step - step)
        q = state.quotients[step] if step < len(state.quotients) else "-"
        rows.append([step, s.old_r, s.r, s.old_s, s.s, q])
    print_table(headers, rows, None)

    # =========================================================================
    # SECTION 3a: Calculate (rollback without quotients)
    # =========================================================================
    print("\n--- 3a. CALCULATE (brute force rollback) ---")
    print("Note: 16-bit requires larger search space, using timeout=300s (5 min), max_q=500")

    recovered = rollback_without_quotients(state, p, timeout_sec=300.0, max_q=500)
    meta = getattr(recovered, '_rollback_meta', {})

    print(f"\nResults:")
    print(f"Candidates found: {meta.get('num_candidates', 0)}")
    print(f"Time: {meta.get('elapsed_sec', 0):.3f}s")
    print(f"Timed out: {meta.get('timed_out', False)}")
    print(f"Quotients recovered: {recovered.quotients if recovered.quotients else 'None'}")
    print(f"Bits determined: {len(recovered.reconstructed_bits)}")

    # Show step candidates log
    if meta.get('step_candidates_log'):
        print("\nStep candidates summary:")
        headers = ["Depth", "Total", "Valid"]
        rows = [[d, t, v] for d, t, v in meta['step_candidates_log'][:20]]  # First 20
        print_table(headers, rows, None)

    # Show candidate arrays
    if meta.get('candidate_old_r'):
        print(f"\nCandidate old_r values: {meta['candidate_old_r'][:10]}")  # First 10
        print(f"Candidate quotient sequences: {meta['candidate_quotients'][:5]}")  # First 5

    if recovered.reconstructed_bits:
        headers = ["Pos", "Bit"]
        rows = [[pos, bit] for pos, bit in sorted(recovered.reconstructed_bits.items())]
        print_table(headers, rows, "Reconstructed Bits")

    # =========================================================================
    # SECTION 3b: Verify
    # =========================================================================
    print("\n--- 3b. VERIFY ---")

    verification = verify_rollback(state, recovered, a, p)

    print(f"Quotients recovered: {verification['quotients_recovered']}")
    print(f"Quotients match: {verification['quotients_match']}")
    print(f"Initial state match: {verification['initial_match']}")
    print(f"Bits determined: {verification['bits_determined']}")
    print(f"Bits correct: {verification['bits_correct']}")
    print(f"Bits wrong: {verification['bits_wrong']}")

    # =========================================================================
    # SECTION 4: Information Loss Analysis
    # =========================================================================
    print("\n--- 4. INFORMATION LOSS ---")

    headers = ["Step", "q", "bits(q)", "Cumulative"]
    rows = []
    total_bits = 0
    for i, q in enumerate(state.quotients):
        bits = max(1, q.bit_length()) if q >= 0 else 1
        total_bits += bits
        rows.append([i + 1, q, bits, total_bits])
    print_table(headers, rows, None)

    print(f"\nTotal bits lost: {total_bits}")
    print(f"Possible previous states without quotients: 2^{total_bits} = {2**total_bits}")
    print(f"Input bits: a={a.bit_length()}, p={p.bit_length()}, total={a.bit_length() + p.bit_length()}")

    print("\n" + "=" * 70)


def analyze_information_loss(a: int, p: int) -> dict:
    """
    Analyze information loss for mod_inverse(a, p).

    Returns dict with:
        - quotients: list of quotients
        - bits_per_step: bits lost per step
        - total_bits: total bits lost
        - steps: number of EEA steps
    """
    state = mod_inverse_full(a, p)

    bits_per_step = []
    for q in state.quotients:
        bits = max(1, q.bit_length()) if q >= 0 else 1
        bits_per_step.append(bits)

    return {
        'quotients': state.quotients,
        'bits_per_step': bits_per_step,
        'total_bits': sum(bits_per_step),
        'steps': len(state.quotients),
        'avg_bits_per_step': sum(bits_per_step) / len(bits_per_step) if bits_per_step else 0
    }


def demo_16bit_samples():
    """Test multiple 16-bit values to understand the pattern."""
    print("\n" + "=" * 70)
    print("16-BIT SAMPLE ANALYSIS")
    print("=" * 70)

    p = TEST_P_16BIT  # 65521, largest 16-bit prime

    # Various 16-bit test values
    test_values = [
        (12345, "12345 (14-bit)"),
        (32768, "32768 (16-bit, 2^15)"),
        (48271, "48271 (16-bit, default)"),
        (65519, "65519 (16-bit, near p)"),
        (7, "7 (3-bit, small)"),
        (255, "255 (8-bit)"),
        (4096, "4096 (13-bit, 2^12)"),
    ]

    headers = ["Value", "bits(a)", "Steps", "bits(q)", "Avg q bits", "Ratio"]
    rows = []

    for a, label in test_values:
        try:
            info = analyze_information_loss(a, p)
            bits_a = a.bit_length()
            bits_p = p.bit_length()
            input_bits = bits_a + bits_p
            ratio = info['total_bits'] / input_bits if input_bits > 0 else 0
            rows.append([
                label,
                bits_a,
                info['steps'],
                info['total_bits'],
                f"{info['avg_bits_per_step']:.2f}",
                f"{ratio:.2f}"
            ])
        except Exception as e:
            rows.append([label, "err", "err", "err", "err", str(e)[:10]])

    print_table(headers, rows, f"Information Loss (p={p})")

    print("\nObservations for 16-bit scale:")
    print("- Steps typically range from 10-20 for 16-bit inputs")
    print("- Total quotient bits ~ bits(a) + bits(p) (continued fraction property)")
    print("- Brute force becomes expensive: O(max_q^steps)")
    print("=" * 70)


def demo_complexity_estimate():
    """Estimate brute force complexity for 16-bit rollback."""
    print("\n" + "=" * 70)
    print("COMPLEXITY ESTIMATE FOR 16-BIT ROLLBACK")
    print("=" * 70)

    a, p = TEST_A_16BIT, TEST_P_16BIT
    state = mod_inverse_full(a, p)

    steps = state.step
    max_q = max(state.quotients)

    print(f"For a={a}, p={p}:")
    print(f"  Steps: {steps}")
    print(f"  Quotients: {state.quotients}")
    print(f"  Max quotient: {max_q}")

    # Estimate search space
    # Without constraints: max_q^steps
    # With constraints: much smaller due to EEA bounds

    naive_space = 100 ** steps  # if max_q=100
    print(f"\nNaive search space (max_q=100): {100}^{steps} = {naive_space:.2e}")
    print(f"Naive search space (max_q=500): {500}^{steps} = {500**steps:.2e}")

    # Actual space is bounded by p
    print(f"\nActual space bounded by p={p}")
    print(f"EEA constraints reduce this significantly")
    print(f"old_r must decrease each step, r must be < old_r")

    print("=" * 70)


if __name__ == "__main__":
    demo()
    demo_16bit_samples()
    demo_complexity_estimate()
