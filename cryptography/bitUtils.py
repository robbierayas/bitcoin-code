"""
Bit-Level Math Utilities for ECDSA

Common mathematical operations shared between ecdsa4bit.py and ecdsaRR.py.

For detailed explanations of why these operations destroy bit relationships,
see reference/bitUtils.md

Operations:
- mod_inverse: Extended Euclidean Algorithm for modular multiplicative inverse
- to_hex/to_bin: Format integers as hex/binary strings
- bit_length: Count significant bits

Complexity Summary:
- mod_inverse: O(log p) time, O(1) space
- All formatting functions: O(n) where n = bit length
"""


def mod_inverse(a: int, p: int) -> int:
    """
    Compute modular multiplicative inverse using Extended Euclidean Algorithm.

    Returns x such that: a * x = 1 (mod p)

    Algorithm:
        Uses the Extended Euclidean Algorithm (EEA) to find x, y where:
            a*x + p*y = gcd(a, p) = 1
        Then x is the modular inverse.

    Why this destroys bit relationships:
        The core operation is integer division: quotient = old_r // r
        Integer division has NO bit-by-bit pattern - it requires comparing
        magnitudes and repeated subtraction. Each iteration's quotient
        depends on ALL bits of both operands, and subsequent iterations
        compound this mixing. See reference/bitUtils.md for details.

    Reversibility:
        - Mathematical: YES - (a^(-1))^(-1) = a, same O(log p) cost
        - Bit-level: NO - cannot trace which input bits affected which output bits

    Args:
        a: Number to invert (must be coprime to p, i.e., gcd(a,p) = 1)
        p: Modulus (typically prime for elliptic curves)

    Returns:
        The modular inverse a^(-1) mod p

    Raises:
        ValueError: If a is 0 or gcd(a, p) != 1 (no inverse exists)

    Example:
        >>> mod_inverse(3, 17)
        6
        >>> (3 * 6) % 17
        1
    """
    if a == 0:
        raise ValueError("Cannot compute inverse of 0")

    # Handle negative inputs
    if a < 0:
        a = a % p

    # Extended Euclidean Algorithm
    # Invariant: old_s * a_original = old_r (mod p)
    old_r, r = a % p, p
    old_s, s = 1, 0

    while r != 0:
        # INTEGER DIVISION - this is where bit relationships are destroyed
        # quotient depends on ALL bits of old_r and r
        quotient = old_r // r

        # Update remainders and coefficients
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    # old_r is now gcd(a, p)
    if old_r != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {p}) = {old_r} != 1")

    return old_s % p


def mod_inverse_fermat(a: int, p: int) -> int:
    """
    Compute modular inverse using Fermat's Little Theorem.

    For prime p: a^(-1) = a^(p-2) mod p

    This is simpler but slower than EEA for large numbers.
    Included for educational comparison.

    Args:
        a: Number to invert
        p: Prime modulus

    Returns:
        The modular inverse a^(-1) mod p

    Note:
        Only works when p is prime. Use mod_inverse() for general case.
    """
    if a == 0:
        raise ValueError("Cannot compute inverse of 0")
    return pow(a, p - 2, p)


# =============================================================================
# Step-based mod_inverse for rollback support
# =============================================================================

from dataclasses import dataclass, replace, field
from typing import Dict


@dataclass
class ModInverseState:
    """
    Represents the state at any point during Extended Euclidean Algorithm.

    Attributes:
        old_r, r: Remainder values (old_r = quotient * r + new_r each step)
        old_s, s: Coefficient values tracking the inverse
        step: Current step number (0 = initial)
        quotients: List of quotients from each step (for rollback)
        reconstructed_bits: Map of bit_position -> bit_value (0 or 1)
            Only contains entries for bits that have been determined.
    """
    old_r: int
    r: int
    old_s: int
    s: int
    step: int = 0
    quotients: list = field(default_factory=list)
    reconstructed_bits: Dict[int, int] = field(default_factory=dict)

    def copy(self) -> 'ModInverseState':
        new_state = replace(self)
        new_state.quotients = self.quotients.copy()
        new_state.reconstructed_bits = self.reconstructed_bits.copy()
        return new_state

    def get_reconstructed_value(self) -> int:
        """Reconstruct value from known bits (unknown bits = 0)."""
        value = 0
        for pos, bit in self.reconstructed_bits.items():
            if bit:
                value |= (1 << pos)
        return value

    def bits_determined(self) -> int:
        """Return count of determined bits."""
        return len(self.reconstructed_bits)


def mod_inverse_full(a: int, p: int) -> ModInverseState:
    """
    Run complete mod_inverse and return final state with all quotients recorded.

    This populates a ModInverseState with the full execution history,
    making it suitable for rollback operations.

    Args:
        a: Number to compute inverse of
        p: Modulus (typically prime)

    Returns:
        Final ModInverseState with:
            - old_r = 1 (gcd), r = 0
            - old_s = inverse (mod p)
            - quotients = list of all quotients used
            - step = number of steps taken

    Raises:
        ValueError: If no inverse exists (gcd != 1)
    """
    state = ModInverseState(old_r=a % p, r=p, old_s=1, s=0, step=0)

    while state.r != 0:
        state, quotient = mod_inverse_step(state)
        state.quotients.append(quotient)

    if state.old_r != 1:
        raise ValueError(f"No inverse: gcd({a}, {p}) = {state.old_r}")

    return state


def mod_inverse_step(state: ModInverseState) -> tuple[ModInverseState, int]:
    """
    Perform ONE step of the Extended Euclidean Algorithm.

    This is the atomic operation where bit relationships are destroyed.
    The integer division quotient = old_r // r mixes ALL bits.

    Args:
        state: Current EEA state (old_r, r, old_s, s, step)

    Returns:
        Tuple of (new_state, quotient)
        - new_state: State after this step
        - quotient: The computed quotient (needed for rollback)

    Raises:
        ValueError: If r == 0 (algorithm complete, no more steps)
    """
    if state.r == 0:
        raise ValueError("Cannot step: r=0 means algorithm is complete")

    # THE CRITICAL OPERATION - integer division destroys bit patterns
    quotient = state.old_r // state.r

    # Compute new values
    new_r = state.old_r - quotient * state.r
    new_s = state.old_s - quotient * state.s

    # Create new state (the swap happens here)
    # Note: quotients list is copied but not appended - caller decides whether to record
    new_state = ModInverseState(
        old_r=state.r,
        r=new_r,
        old_s=state.s,
        s=new_s,
        step=state.step + 1,
        quotients=state.quotients.copy()
    )

    return new_state, quotient


def to_hex(val: int, width: int = 2) -> str:
    """
    Convert integer to hex string with 0x prefix.

    Args:
        val: Integer value
        width: Minimum hex digits (zero-padded)

    Returns:
        Hex string like "0x0F"

    Example:
        >>> to_hex(15, 2)
        '0x0F'
        >>> to_hex(256, 4)
        '0x0100'
    """
    return f"0x{val:0{width}X}"


def to_bin(val: int, width: int = 8) -> str:
    """
    Convert integer to binary string.

    Args:
        val: Integer value
        width: Minimum binary digits (zero-padded)

    Returns:
        Binary string like "00001111"

    Example:
        >>> to_bin(15, 8)
        '00001111'
    """
    return f"{val:0{width}b}"


def bit_length(val: int) -> int:
    """
    Return the number of bits needed to represent val.

    Args:
        val: Non-negative integer

    Returns:
        Number of significant bits

    Example:
        >>> bit_length(15)  # 1111 in binary
        4
        >>> bit_length(16)  # 10000 in binary
        5
    """
    if val == 0:
        return 0
    return val.bit_length()


def hex_to_int(hex_str: str) -> int:
    """
    Convert hex string to integer.

    Handles with or without '0x' prefix.

    Args:
        hex_str: Hex string like "0x1F" or "1F"

    Returns:
        Integer value
    """
    if hex_str.startswith('0x') or hex_str.startswith('0X'):
        return int(hex_str, 16)
    return int(hex_str, 16)


def int_to_bytes(val: int, length: int = None) -> bytes:
    """
    Convert integer to big-endian bytes.

    Args:
        val: Non-negative integer
        length: Byte length (auto-calculated if None)

    Returns:
        Bytes representation
    """
    if length is None:
        length = (val.bit_length() + 7) // 8
        if length == 0:
            length = 1
    return val.to_bytes(length, byteorder='big')


def bytes_to_int(b: bytes) -> int:
    """
    Convert big-endian bytes to integer.

    Args:
        b: Bytes to convert

    Returns:
        Integer value
    """
    return int.from_bytes(b, byteorder='big')


def print_table(headers: list, rows: list, title: str = None):
    """
    Print a formatted ASCII table.

    Args:
        headers: List of column header strings
        rows: List of row data (each row is a list of values)
        title: Optional title to print above the table

    Example:
        >>> headers = ["Step", "Value", "Status"]
        >>> rows = [[0, 123, "OK"], [1, 456, "OK"]]
        >>> print_table(headers, rows, "Results")
    """
    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Build format string
    row_fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"
    separator = "+-" + "-+-".join("-" * w for w in widths) + "-+"

    # Print table
    if title:
        print(f"\n{title}")
    print(separator)
    print(row_fmt.format(*[str(h) for h in headers]))
    print(separator)
    for row in rows:
        print(row_fmt.format(*[str(c) for c in row]))
    print(separator)


# =============================================================================
# Demonstration / Testing
# =============================================================================

def demo_mod_inverse():
    """Demonstrate mod_inverse with step-by-step output."""
    print("=" * 70)
    print("MODULAR INVERSE DEMONSTRATION")
    print("=" * 70)

    a, p = 3, 17

    print(f"\nComputing mod_inverse({a}, {p})")
    print(f"Find x where {a} * x = 1 (mod {p})")

    print("\nExtended Euclidean Algorithm trace:")
    print("-" * 50)

    # Manual trace
    old_r, r = a % p, p
    old_s, s = 1, 0
    step = 0

    print(f"Initial: old_r={old_r}, r={r}, old_s={old_s}, s={s}")

    while r != 0:
        step += 1
        quotient = old_r // r

        new_r = old_r - quotient * r
        new_s = old_s - quotient * s

        print(f"\nStep {step}:")
        print(f"  quotient = {old_r} // {r} = {quotient}")
        print(f"  old_r, r = {r}, {old_r} - {quotient}*{r} = {r}, {new_r}")
        print(f"  old_s, s = {s}, {old_s} - {quotient}*{s} = {s}, {new_s}")

        old_r, r = r, new_r
        old_s, s = s, new_s

    result = old_s % p
    print(f"\nResult: {result}")
    print(f"Verify: {a} * {result} = {a * result} = {(a * result) % p} (mod {p})")

    print("\n" + "-" * 50)
    print("KEY INSIGHT: Each quotient depends on ALL bits of old_r and r.")
    print("The division operation has no bit-by-bit pattern.")
    print("=" * 70)


def demo_bit_destruction():
    """Show how mod_inverse destroys bit patterns."""
    print("\n" + "=" * 70)
    print("BIT PATTERN DESTRUCTION")
    print("=" * 70)

    p = 17
    print(f"\nField: Z_{p}")
    print(f"\n{'a':>4} {'bin(a)':>10} {'a^(-1)':>6} {'bin(a^-1)':>10} {'correlation'}")
    print("-" * 50)

    for a in range(1, p):
        inv = mod_inverse(a, p)
        bin_a = to_bin(a, 5)
        bin_inv = to_bin(inv, 5)

        # Count matching bits (meaningless but shows no pattern)
        matches = sum(1 for i in range(5) if bin_a[i] == bin_inv[i])

        print(f"{a:>4} {bin_a:>10} {inv:>6} {bin_inv:>10}     {matches}/5 bits match")

    print("\nNote: Matching bits is random (~2.5/5 expected by chance)")
    print("There is NO predictable bit relationship.")
    print("=" * 70)


if __name__ == "__main__":
    demo_mod_inverse()
    demo_bit_destruction()
