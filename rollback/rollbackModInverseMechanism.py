"""
Mod inverse step rollback mechanism.

This module implements rollback for the Extended Euclidean Algorithm (EEA)
used in mod_inverse. The key insight is that integer division destroys
bit relationships, but rollback is possible if quotients are recorded.

The mechanism operates on mod_inverse_step, not the full mod_inverse function.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Optional
from rollback.rollbackMechanism import RollbackMechanism
from cryptography.bitUtils import ModInverseState, mod_inverse_step, print_table


def mod_inverse_step_reverse(state: ModInverseState, quotient: int) -> ModInverseState:
    """
    Reverse ONE step of the Extended Euclidean Algorithm.

    Given the current state and the quotient that was used to get here,
    reconstruct the previous state.

    The key insight: Without the quotient, reversal is NOT unique!
    Multiple previous states could lead to the same current state.

    Args:
        state: Current EEA state (result of a forward step)
        quotient: The quotient that was used in the forward step

    Returns:
        The previous state before that step was applied
    """
    # Reverse the swap and arithmetic
    # Forward was: new_old_r = old_r, new_r = old_r - q*r -> swap -> (r, old_r - q*r)
    # So: state.old_r = prev.r, state.r = prev.old_r - q * prev.r
    # Therefore: prev.r = state.old_r
    #           prev.old_r = state.r + q * state.old_r

    prev_r = state.old_r

    prev_old_r = state.r + quotient * state.old_r

    prev_s = state.old_s
    prev_old_s = state.s + quotient * state.old_s

    return ModInverseState(
        old_r=prev_old_r,
        r=prev_r,
        old_s=prev_old_s,
        s=prev_s,
        step=state.step - 1
    )


class ModInverseRollbackMechanism(RollbackMechanism):
    """
    Rollback mechanism for mod_inverse step operations.

    Records quotients during forward execution to enable perfect rollback.
    Demonstrates that EEA is reversible when intermediate values are known,
    but information-theoretically irreversible without them.
    """

    def __init__(self, a: int, p: int):
        """
        Initialize the mod inverse rollback mechanism.

        Args:
            a: Number to compute inverse of
            p: Modulus (typically prime)
        """
        super().__init__(target=(a, p))
        self.a = a
        self.p = p
        self.initial_state = ModInverseState(a % p, p, 1, 0, step=0)
        self.quotients: List[int] = []
        self.states: List[ModInverseState] = [self.initial_state.copy()]
        self.final_state: Optional[ModInverseState] = None

    def run(self):
        """
        Execute forward mod_inverse, recording all steps.

        Returns:
            The modular inverse a^(-1) mod p
        """
        state = self.initial_state.copy()

        while state.r != 0:
            state, quotient = mod_inverse_step(state)
            self.quotients.append(quotient)
            self.states.append(state.copy())

        self.final_state = state

        if state.old_r != 1:
            raise ValueError(f"No inverse: gcd({self.a}, {self.p}) = {state.old_r}")

        self.result = state.old_s % self.p
        return self.result

    def rollback(self, steps: int = 1) -> ModInverseState:
        """
        Roll back from final state by given number of steps.

        Args:
            steps: Number of steps to reverse (default 1)

        Returns:
            The state after rolling back
        """
        if self.final_state is None:
            raise ValueError("Must call run() before rollback()")

        if steps > len(self.quotients):
            raise ValueError(f"Cannot rollback {steps} steps, only {len(self.quotients)} recorded")

        state = self.final_state.copy()

        # Roll back using recorded quotients (in reverse order)
        for i in range(steps):
            q_idx = len(self.quotients) - 1 - i
            state = mod_inverse_step_reverse(state, self.quotients[q_idx])

        return state

    def rollback_to_step(self, target_step: int) -> ModInverseState:
        """
        Roll back to a specific step number.

        Args:
            target_step: Step number to return to (0 = initial)

        Returns:
            State at that step
        """
        current_step = self.final_state.step
        steps_back = current_step - target_step
        return self.rollback(steps_back)

    def verify_rollback(self) -> bool:
        """
        Verify that rollback correctly reconstructs all states.

        Returns:
            True if all states match, False otherwise
        """
        for target_step in range(len(self.states)):
            rolled_back = self.rollback_to_step(target_step)
            original = self.states[target_step]

            if (rolled_back.old_r != original.old_r or
                rolled_back.r != original.r or
                rolled_back.old_s != original.old_s or
                rolled_back.s != original.s):
                return False

        return True


def brute_force_bits(final_state: ModInverseState, num_steps: int,
                     known_p: int = None, max_q: int = 20,
                     target_bits: int = None, max_candidates: int = 10000,
                     verbose: bool = False):
    """
    Brute force possible quotient sequences to determine bits of original input.

    From the final state, enumerate valid quotient combinations and track
    which bits are consistent across ALL valid reconstructions.

    Args:
        final_state: The final state after mod_inverse completed
        num_steps: Number of steps to reverse
        known_p: The modulus p (if known, used to validate candidates)
        max_q: Maximum quotient value to try per step
        target_bits: Stop when this many bits are determined (None = find all)
        max_candidates: Maximum candidates to evaluate
        verbose: Print progress

    Returns:
        Dict with:
            - reconstructed_bits: {position: bit_value} for determined bits
            - candidates: list of all valid (old_r, quotient_sequence) pairs
            - bits_determined: count of determined bits
    """
    candidates = []

    def recurse(state: ModInverseState, depth: int, quotients: list):
        """Recursively try quotient values."""
        if len(candidates) >= max_candidates:
            return

        if depth == 0:
            # Reached initial state - validate it
            # Initial state should have: old_s=1, s=0
            # And if we know p: r should equal p
            if state.old_s != 1 or state.s != 0:
                return  # Invalid initial state

            if known_p is not None and state.r != known_p:
                return  # r must equal p at initial state

            # Valid candidate found
            candidates.append((state.old_r, state.r, quotients.copy()))
            return

        # Try different quotient values
        for q in range(0, max_q + 1):
            # Reverse one step with this quotient
            prev_r = state.old_r
            prev_old_r = state.r + q * state.old_r
            prev_s = state.old_s
            prev_old_s = state.s + q * state.old_s

            # Validity checks
            # 1. In EEA, old_r > r (remainders decrease), except possibly first step
            if q > 0 and prev_old_r <= prev_r:
                continue

            # 2. old_r should be less than or equal to p if we know it
            if known_p is not None and prev_old_r > known_p:
                continue

            prev_state = ModInverseState(
                old_r=prev_old_r,
                r=prev_r,
                old_s=prev_old_s,
                s=prev_s,
                step=state.step - 1
            )

            recurse(prev_state, depth - 1, quotients + [q])

    # Start recursion
    recurse(final_state, num_steps, [])

    if verbose:
        print(f"Found {len(candidates)} candidate reconstructions")

    if not candidates:
        return {
            'reconstructed_bits': {},
            'candidates': [],
            'bits_determined': 0
        }

    # Find bits that are consistent across ALL candidates
    reconstructed_bits = {}
    max_bit = max(c[0].bit_length() for c in candidates) if candidates else 0

    for bit_pos in range(max_bit + 1):
        bit_values = set()
        for old_r, r, qs in candidates:
            bit_val = (old_r >> bit_pos) & 1
            bit_values.add(bit_val)

        if len(bit_values) == 1:
            # This bit is the same in ALL candidates - it's determined!
            reconstructed_bits[bit_pos] = bit_values.pop()

            if target_bits and len(reconstructed_bits) >= target_bits:
                break

    return {
        'reconstructed_bits': reconstructed_bits,
        'candidates': candidates,
        'bits_determined': len(reconstructed_bits)
    }


def demo():
    """Demonstrate the mod_inverse step rollback mechanism."""
    print("=" * 70)
    print("MOD_INVERSE STEP ROLLBACK MECHANISM")
    print("=" * 70)

    a, p = 7, 23

    # Create mechanism and run
    mechanism = ModInverseRollbackMechanism(a, p)
    result = mechanism.run()

    print(f"\nmod_inverse({a}, {p}) = {result}")
    print(f"Verify: {a} * {result} mod {p} = {(a * result) % p}")

    # Forward execution table
    headers = ["Step", "old_r", "r", "old_s", "s", "q"]
    rows = []
    for i, state in enumerate(mechanism.states):
        q = mechanism.quotients[i] if i < len(mechanism.quotients) else "-"
        rows.append([i, state.old_r, state.r, state.old_s, state.s, q])
    print_table(headers, rows, "Forward Execution")

    # Rollback demonstration table
    final = mechanism.final_state
    headers = ["Back", "old_r", "r", "old_s", "s", "Match"]
    rows = []
    for steps_back in range(1, len(mechanism.quotients) + 1):
        rolled = mechanism.rollback(steps_back)
        original = mechanism.states[len(mechanism.states) - 1 - steps_back]
        match = "OK" if (rolled.old_r == original.old_r and
                        rolled.r == original.r) else "FAIL"
        rows.append([f"-{steps_back}", rolled.old_r, rolled.r,
                    rolled.old_s, rolled.s, match])
    print_table(headers, rows, "Rollback (from final state)")

    # Verification
    status = "PASS" if mechanism.verify_rollback() else "FAIL"
    print(f"\nVerification: {status}")

    # Information loss analysis
    import math
    headers = ["Step", "q", "bits(q)", "Cumulative"]
    rows = []
    total_bits = 0
    for i, q in enumerate(mechanism.quotients):
        # Bits needed to encode quotient: ceil(log2(q+1)) for q>=0
        # q=0 needs 1 bit, q=1 needs 1 bit, q=2-3 needs 2 bits, etc.
        bits = max(1, q.bit_length()) if q >= 0 else 1
        total_bits += bits
        rows.append([i + 1, q, bits, total_bits])
    print_table(headers, rows, "Information Loss Per Step")

    print(f"\nTotal bits lost: {total_bits}")
    print(f"Possible previous states without quotients: 2^{total_bits} = {2**total_bits}")

    # Ambiguity table
    print(f"\nFinal: old_r={final.old_r}, r={final.r}")
    headers = ["q", "prev.old_r", "Formula"]
    rows = []
    for q in range(1, 6):
        val = final.r + q * final.old_r
        formula = f"{final.r} + {q}*{final.old_r}"
        rows.append([q, val, formula])
    print_table(headers, rows, "Possible previous states (last step only)")

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
    mechanism = ModInverseRollbackMechanism(a, p)
    mechanism.run()

    bits_per_step = []
    for q in mechanism.quotients:
        bits = max(1, q.bit_length()) if q >= 0 else 1
        bits_per_step.append(bits)

    return {
        'quotients': mechanism.quotients,
        'bits_per_step': bits_per_step,
        'total_bits': sum(bits_per_step),
        'steps': len(mechanism.quotients),
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


def brute_force_single_step(after_state: ModInverseState, max_q: int = 20):
    """
    Brute force ONE mod_inverse_step to find possible previous states.

    Given the state AFTER one step, find all possible BEFORE states
    by trying different quotient values.

    Args:
        after_state: State after mod_inverse_step was applied
        max_q: Maximum quotient to try

    Returns:
        Dict with:
            - candidates: list of (prev_old_r, quotient) pairs
            - reconstructed_bits: {pos: bit} for bits consistent across all candidates
    """
    candidates = []

    for q in range(0, max_q + 1):
        # Reverse: prev_old_r = after.r + q * after.old_r
        prev_old_r = after_state.r + q * after_state.old_r

        # Validity: in EEA, old_r > r (remainders decrease)
        # after.old_r was prev.r, so prev_old_r should be > prev_r = after.old_r
        if q > 0 and prev_old_r <= after_state.old_r:
            continue

        candidates.append((prev_old_r, q))

    # Find consistent bits across all candidates
    reconstructed_bits = {}
    if candidates:
        max_bit = max(c[0].bit_length() for c in candidates)
        for pos in range(max_bit):
            bits = set((c[0] >> pos) & 1 for c in candidates)
            if len(bits) == 1:
                reconstructed_bits[pos] = bits.pop()

    return {
        'candidates': candidates,
        'reconstructed_bits': reconstructed_bits,
        'bits_determined': len(reconstructed_bits)
    }


def demo_single_step_brute_force():
    """Demo brute force on a SINGLE mod_inverse_step, starting from final state."""
    print("\n" + "=" * 70)
    print("SINGLE STEP BRUTE FORCE (from final state)")
    print("=" * 70)

    # Run full mod_inverse to get all states
    mechanism = ModInverseRollbackMechanism(7, 23)
    mechanism.run()

    print("\nForward execution:")
    headers = ["Step", "old_r", "r", "old_s", "s", "q"]
    rows = []
    for i, state in enumerate(mechanism.states):
        q = mechanism.quotients[i] if i < len(mechanism.quotients) else "-"
        rows.append([i, state.old_r, state.r, state.old_s, state.s, q])
    print_table(headers, rows, None)

    # Start from FINAL state and reverse ONE step
    final = mechanism.final_state
    print(f"\n--- Reversing from final state ---")
    print(f"Final: old_r={final.old_r}, r={final.r}")
    print(f"Formula: prev_old_r = r + q * old_r = {final.r} + q * {final.old_r} = q")
    print(f"So: quotient = prev_old_r directly!")

    # The previous state was step 3
    actual_prev = mechanism.states[-2]  # Second to last
    actual_q = mechanism.quotients[-1]  # Last quotient

    print(f"\nActual previous: old_r={actual_prev.old_r}, r={actual_prev.r}")
    print(f"Actual quotient: {actual_q}")

    # Brute force: try different q values
    print("\n--- Brute force candidates ---")
    headers = ["q", "prev_old_r", "prev_r", "valid?"]
    rows = []
    for q in range(1, 15):  # q >= 1 since prev_old_r > prev_r = 1
        prev_old_r = final.r + q * final.old_r  # = 0 + q * 1 = q
        prev_r = final.old_r  # = 1
        valid = prev_old_r > prev_r  # EEA constraint
        marker = " <-- actual" if q == actual_q else ""
        rows.append([q, prev_old_r, prev_r, f"{'yes' if valid else 'no'}{marker}"])
    print_table(headers, rows, "Candidates for step 3 -> 4")

    # Key insight
    print("\nKey insight:")
    print("  At final state (old_r=1, r=0), quotient = prev_old_r")
    print("  Constraint: prev_old_r > 1 (since prev_r = 1)")
    print("  Without more constraints, prev_old_r can be 2, 3, 4, ...")

    # Now show what bits we can determine
    print("\n--- Bit analysis of prev_old_r ---")
    candidates = list(range(2, 15))  # Valid prev_old_r values

    reconstructed = {}
    max_bit = max(c.bit_length() for c in candidates)
    for pos in range(max_bit):
        bits = set((c >> pos) & 1 for c in candidates)
        if len(bits) == 1:
            reconstructed[pos] = bits.pop()

    headers = ["Pos", "Actual", "Determined"]
    rows = []
    for pos in range(max_bit):
        actual = (actual_prev.old_r >> pos) & 1
        det = reconstructed.get(pos, "?")
        rows.append([pos, actual, det])
    print_table(headers, rows, None)

    print(f"\nBits determined: {len(reconstructed)} / {actual_prev.old_r.bit_length()}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo()
    demo_single_step_brute_force()
    demo_bitcoin_scale()
