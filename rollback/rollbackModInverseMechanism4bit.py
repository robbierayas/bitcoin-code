"""
Mod inverse step rollback mechanism.

This module implements rollback for the Extended Euclidean Algorithm (EEA)
used in mod_inverse. The key insight is that integer division destroys
bit relationships, but rollback is possible if quotients are recorded.

The mechanism operates on mod_inverse_step, not the full mod_inverse function.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Optional, Dict
from cryptography.bitUtils import ModInverseState, mod_inverse_full, print_table


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
                                timeout_sec: float = 30.0,
                                max_q: int = 100,
                                max_candidates: int = 100000) -> ModInverseState:
    """
    Attempt rollback WITHOUT quotients (brute force).

    Makes a copy, clears quotients, tries to recover them via brute force.
    Returns state with recovered quotients and reconstructed_bits.

    Args:
        state: Final state from mod_inverse_full (quotients will be ignored)
        known_p: The modulus p (used to validate candidates)
        timeout_sec: Timeout in seconds (default 30)
        max_q: Maximum quotient value to try per step
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

    candidates = []  # List of (old_r, r, quotient_sequence)

    def recurse(s: ModInverseState, depth: int, quotients: list):
        """Recursively try quotient values."""
        # Check timeout
        if time.time() - start_time > timeout_sec:
            return
        if len(candidates) >= max_candidates:
            return

        if depth == 0:
            # Reached initial state - validate
            if s.old_s != 1 or s.s != 0:
                return
            if s.r != known_p:
                return
            candidates.append((s.old_r, s.r, quotients.copy()))
            return

        # Try different quotient values
        for q in range(0, max_q + 1):
            if time.time() - start_time > timeout_sec:
                return

            prev_old_r = s.r + q * s.old_r
            prev_r = s.old_r
            prev_old_s = s.s + q * s.old_s
            prev_s = s.old_s

            # EEA constraint: old_r > r (except possibly q=0)
            if q > 0 and prev_old_r <= prev_r:
                continue
            if prev_old_r > known_p:
                continue

            prev_state = ModInverseState(
                old_r=prev_old_r, r=prev_r,
                old_s=prev_old_s, s=prev_s,
                step=s.step - 1
            )
            recurse(prev_state, depth - 1, [q] + quotients)

    # Run brute force
    recurse(work_state, num_steps, [])

    elapsed = time.time() - start_time
    timed_out = elapsed >= timeout_sec

    # Build result state
    result = state.copy()
    result.quotients = []
    result.reconstructed_bits = {}

    if candidates:
        # If exactly one candidate, we found the quotients
        if len(candidates) == 1:
            result.quotients = candidates[0][2]

        # Find bits consistent across ALL candidates
        max_bit = max(c[0].bit_length() for c in candidates)
        for pos in range(max_bit):
            bits = set((c[0] >> pos) & 1 for c in candidates)
            if len(bits) == 1:
                result.reconstructed_bits[pos] = bits.pop()

    # Store metadata
    result._rollback_meta = {
        'candidates': len(candidates),
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
    """Demonstrate the mod_inverse step rollback mechanism."""
    print("=" * 70)
    print("MOD_INVERSE STEP ROLLBACK MECHANISM")
    print("=" * 70)

    a, p = 7, 23

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

    recovered = rollback_without_quotients(state, p, timeout_sec=30.0)
    meta = getattr(recovered, '_rollback_meta', {})

    print(f"Candidates found: {meta.get('candidates', 0)}")
    print(f"Time: {meta.get('elapsed_sec', 0):.3f}s")
    print(f"Timed out: {meta.get('timed_out', False)}")
    print(f"Quotients recovered: {recovered.quotients if recovered.quotients else 'None'}")
    print(f"Bits determined: {len(recovered.reconstructed_bits)}")

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


def demo_bitcoin_scale():
    """Show information loss at Bitcoin scale (256-bit)."""
    print("\n" + "=" * 70)
    print("INFORMATION LOSS AT BITCOIN SCALE")
    print("=" * 70)

    # secp256k1 prime
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    # Sample values at different bit sizes
    # Note: bits(a) + bits(p) ≈ total bits in quotients (they encode the same info)
    test_cases = [
        (7, 23, "a=7, p=23"),
        (12345, 65537, "a=12345, p=65537"),
        (2**31 - 1, 2**31 + 11, "~31-bit"),
        (2**63 - 25, 2**64 - 59, "~64-bit"),
        (2**127 - 1, 2**128 - 159, "~128-bit"),
        (2**255 - 19, p, "~256-bit (Bitcoin)"),
    ]

    headers = ["Inputs", "bits(a)", "bits(p)", "Steps", "bits(q)", "Ratio"]
    rows = []

    for a, mod, label in test_cases:
        try:
            info = analyze_information_loss(a, mod)
            bits_a = a.bit_length()
            bits_p = mod.bit_length()
            input_bits = bits_a + bits_p
            ratio = info['total_bits'] / input_bits if input_bits > 0 else 0
            rows.append([
                label,
                bits_a,
                bits_p,
                info['steps'],
                info['total_bits'],
                f"{ratio:.2f}"
            ])
        except Exception as e:
            rows.append([label, "err", "err", "err", "err", str(e)[:10]])

    print_table(headers, rows, "Information Loss by Input Size")

    # Explanation
    print("\nKey insight: bits(quotients) ~ bits(a) + bits(p)")
    print("The quotients ARE the continued fraction of a/p.")
    print("They encode the same information as the inputs, just rearranged.")
    print("\nRatio ~0.5 means quotients encode about half the input bits.")
    print("Ratio ~1.0 would mean quotients = inputs (perfect encoding).")
    print("=" * 70)


if __name__ == "__main__":
    demo()
    demo_bitcoin_scale()
