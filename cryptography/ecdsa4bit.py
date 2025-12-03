"""
4-bit ECDSA Implementation for Educational Purposes

This implements ECDSA over a tiny elliptic curve where private keys are 4 bits.
Perfect for understanding the math and testing rollback/reverse engineering approaches.

=== WHERE DO THE PARAMETERS COME FROM? ===

ECDSA requires an elliptic curve over a finite field. We need:
1. A prime p (field size) - arithmetic is done mod p
2. Curve equation: y^2 = x^3 + ax + b (mod p)
3. A generator point G on the curve
4. The order N (how many times you add G before getting back to infinity)

For "4-bit ECDSA", we want private keys d to be 4 bits (0x1 to 0xF = 1 to 15).

CHOSEN PARAMETERS:
- p = 0x11 (17) - Smallest prime giving a curve with enough points
- a = 0x02, b = 0x02 - Curve: y^2 = x^3 + 2x + 2 (mod 17)
- G = (0x05, 0x01) - Generator point
- N = 0x13 (19) - Curve order (number of points including infinity)

WHY THESE VALUES?
- p must be prime for finite field arithmetic to work
- The curve must have prime order N for security (prevents small subgroup attacks)
- We found this curve by searching for one where N is prime
- Private keys 0x01-0x0F (1-15) work fine since they're all < N

In real Bitcoin ECDSA (secp256k1):
- p = 0xFFFFFFFF...FFFFFC2F (256-bit prime)
- N = 0xFFFFFFFF...D0364141 (256-bit, also prime)
- Private keys are 256 bits (32 bytes)

For bit-level math explanations, see reference/bitUtils.md
"""

from typing import Tuple, Optional, List
import random
import sys
import os

# Import common math utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cryptography.bitUtils import mod_inverse, to_hex as _to_hex, to_bin


# =============================================================================
# CURVE PARAMETERS (all in hex for clarity)
# =============================================================================

# Prime field size: p = 17 = 0x11
# Arithmetic is done modulo this prime
P = 0x11

# Curve coefficients for y² = x³ + ax + b (mod p)
A = 0x02  # a = 2
B = 0x02  # b = 2

# Generator point G - a point on the curve that generates all other points
# G = (5, 1) = (0x05, 0x01)
G = (0x05, 0x01)

# Order of the curve - total number of points (including point at infinity)
# N = 19 = 0x13
# This means: N * G = O (point at infinity)
N = 0x13

# Point at infinity (identity element for point addition)
INFINITY = None

# Maximum 4-bit private key value
MAX_4BIT = 0x0F  # 15


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def to_hex(val: int, width: int = 2) -> str:
    """Convert integer to hex string with 0x prefix (wrapper for bitUtils)."""
    return _to_hex(val, width)


def point_to_hex(point: Optional[Tuple[int, int]]) -> str:
    """Convert point to hex string representation."""
    if point is None:
        return "O (infinity)"
    return f"({to_hex(point[0])}, {to_hex(point[1])})"


# mod_inverse is imported from bitUtils
# See reference/bitUtils.md for detailed explanation of why it destroys bit relationships


# =============================================================================
# ELLIPTIC CURVE OPERATIONS
# =============================================================================

def is_on_curve(point: Optional[Tuple[int, int]]) -> bool:
    """Check if a point lies on the elliptic curve y² = x³ + ax + b (mod p)."""
    if point is None:
        return True  # Point at infinity is on the curve

    x, y = point
    left = (y * y) % P
    right = (x * x * x + A * x + B) % P
    return left == right


def point_add(p1: Optional[Tuple[int, int]],
              p2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    """
    Add two points on the elliptic curve using the group law.
    Returns p1 + p2
    """
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    # Points are inverses -> result is infinity
    if x1 == x2 and (y1 + y2) % P == 0:
        return INFINITY

    # Calculate slope (lambda)
    if x1 == x2 and y1 == y2:
        # Point doubling: lambda = (3x² + a) / (2y)
        if y1 == 0:
            return INFINITY
        numerator = (3 * x1 * x1 + A) % P
        denominator = (2 * y1) % P
    else:
        # Point addition: lambda = (y2 - y1) / (x2 - x1)
        numerator = (y2 - y1) % P
        denominator = (x2 - x1) % P

    slope = (numerator * mod_inverse(denominator, P)) % P

    # New point coordinates
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P

    return (x3, y3)


def scalar_multiply(k: int, point: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    """
    Multiply a point by a scalar using double-and-add algorithm.
    Returns k * point (point added to itself k times)
    """
    if k == 0 or point is None:
        return INFINITY

    if k < 0:
        k = -k
        point = (point[0], (-point[1]) % P)

    result = INFINITY
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result


def generate_all_points() -> List[Optional[Tuple[int, int]]]:
    """Generate all points on the curve by enumeration."""
    points = [INFINITY]

    for x in range(P):
        y_squared = (x * x * x + A * x + B) % P
        for y in range(P):
            if (y * y) % P == y_squared:
                points.append((x, y))

    return points


# =============================================================================
# ECDSA OPERATIONS
# =============================================================================

def generate_keypair(private_key: Optional[int] = None) -> Tuple[int, Tuple[int, int]]:
    """
    Generate an ECDSA keypair.

    Args:
        private_key: 4-bit private key (0x01-0x0F). If None, generates random.

    Returns:
        (private_key, public_key) where public_key = private_key * G
    """
    if private_key is None:
        private_key = random.randint(0x01, min(MAX_4BIT, N - 1))

    if not (0x01 <= private_key < N):
        raise ValueError(f"Private key must be in range [0x01, {to_hex(N-1)}]")

    public_key = scalar_multiply(private_key, G)
    return (private_key, public_key)


def sign(private_key: int, message_hash: int, k: Optional[int] = None) -> Tuple[int, int]:
    """
    Sign a message hash using ECDSA.

    Args:
        private_key: Signer's private key (0x01-0x0F)
        message_hash: Hash of message (will be reduced mod N)
        k: Nonce (MUST be random and secret in real use!)

    Returns:
        (r, s) signature tuple
    """
    z = message_hash % N

    while True:
        k_val = k if k is not None else random.randint(0x01, N - 1)

        # R = k * G
        R = scalar_multiply(k_val, G)
        if R is None:
            if k is not None:
                raise ValueError("Invalid k")
            continue

        r = R[0] % N
        if r == 0:
            if k is not None:
                raise ValueError("Invalid k: r = 0")
            continue

        # s = k^(-1) * (z + r * d) mod N
        k_inv = mod_inverse(k_val, N)
        s = (k_inv * (z + r * private_key)) % N

        if s == 0:
            if k is not None:
                raise ValueError("Invalid k: s = 0")
            continue

        return (r, s)


def verify(public_key: Tuple[int, int], message_hash: int, signature: Tuple[int, int]) -> bool:
    """
    Verify an ECDSA signature.

    Args:
        public_key: Signer's public key (point on curve)
        message_hash: Hash of message
        signature: (r, s) tuple

    Returns:
        True if valid, False otherwise
    """
    r, s = signature

    if not (0x01 <= r < N and 0x01 <= s < N):
        return False

    if not is_on_curve(public_key):
        return False

    z = message_hash % N

    # w = s^(-1) mod N
    w = mod_inverse(s, N)

    # u1 = z * w mod N, u2 = r * w mod N
    u1 = (z * w) % N
    u2 = (r * w) % N

    # R' = u1 * G + u2 * Q
    R_prime = point_add(scalar_multiply(u1, G), scalar_multiply(u2, public_key))

    if R_prime is None:
        return False

    # Valid if R'.x mod N == r
    return R_prime[0] % N == r


# =============================================================================
# DEMONSTRATION / DIAGNOSTICS
# =============================================================================

def print_curve_info():
    """Print curve parameters and all points in hex."""
    print("=" * 70)
    print("4-BIT ECDSA CURVE PARAMETERS")
    print("=" * 70)
    print(f"\nField prime:     p = {to_hex(P)} ({P})")
    print(f"Curve equation:  y^2 = x^3 + {to_hex(A)}*x + {to_hex(B)} (mod {to_hex(P)})")
    print(f"Generator:       G = {point_to_hex(G)}")
    print(f"Curve order:     N = {to_hex(N)} ({N})")
    print(f"4-bit key range: {to_hex(0x01)} to {to_hex(MAX_4BIT)}")

    points = generate_all_points()
    print(f"\nTotal points on curve: {len(points)}")

    print("\n--- All Points (hex) ---")
    for i, pt in enumerate(points):
        print(f"  [{to_hex(i)}] {point_to_hex(pt)}")

    print("\n--- Scalar Multiples of G ---")
    print("  k      | k * G")
    print("  " + "-" * 30)
    for k in range(0x01, N + 1):
        kG = scalar_multiply(k, G)
        print(f"  {to_hex(k, 2)}     | {point_to_hex(kG)}")

    print("=" * 70)


def demo():
    """Demonstrate ECDSA with hex output."""
    print("\n" + "=" * 70)
    print("4-BIT ECDSA DEMONSTRATION (HEX)")
    print("=" * 70)

    # Keypair
    d = 0x07  # Private key: 4 bits = 0111
    _, Q = generate_keypair(d)

    print(f"\nPrivate key d = {to_hex(d)} (binary: {bin(d)[2:].zfill(4)})")
    print(f"Public key  Q = d * G = {point_to_hex(Q)}")

    # Sign
    z = 0x0B  # Message hash
    k = 0x03  # Nonce (fixed for demo - NEVER do this in real code!)

    print(f"\nMessage hash z = {to_hex(z)}")
    print(f"Nonce        k = {to_hex(k)}")

    r, s = sign(d, z, k)
    print(f"\nSignature:")
    print(f"  r = {to_hex(r)}")
    print(f"  s = {to_hex(s)}")

    # Verify
    valid = verify(Q, z, (r, s))
    print(f"\nSignature valid: {valid}")

    # Show math
    print("\n--- Signature Math (hex) ---")
    R = scalar_multiply(k, G)
    print(f"R = k * G = {to_hex(k)} * G = {point_to_hex(R)}")
    print(f"r = R.x mod N = {to_hex(R[0])} mod {to_hex(N)} = {to_hex(r)}")

    k_inv = mod_inverse(k, N)
    print(f"k^(-1) mod N = {to_hex(k_inv)}")

    inner = (z + r * d) % N
    print(f"z + r*d = {to_hex(z)} + {to_hex(r)}*{to_hex(d)} = {to_hex(inner)} (mod N)")
    print(f"s = k^(-1) * (z + r*d) = {to_hex(k_inv)} * {to_hex(inner)} = {to_hex(s)} (mod N)")

    print("\n--- Verification Math (hex) ---")
    w = mod_inverse(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    print(f"w  = s^(-1) mod N = {to_hex(w)}")
    print(f"u1 = z * w mod N  = {to_hex(u1)}")
    print(f"u2 = r * w mod N  = {to_hex(u2)}")

    R1 = scalar_multiply(u1, G)
    R2 = scalar_multiply(u2, Q)
    R_prime = point_add(R1, R2)
    print(f"u1 * G = {point_to_hex(R1)}")
    print(f"u2 * Q = {point_to_hex(R2)}")
    print(f"R' = u1*G + u2*Q = {point_to_hex(R_prime)}")
    print(f"R'.x mod N = {to_hex(R_prime[0] % N)} == r = {to_hex(r)} ? {R_prime[0] % N == r}")

    print("=" * 70)


if __name__ == "__main__":
    print_curve_info()
    demo()
