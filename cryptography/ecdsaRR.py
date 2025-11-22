"""
Custom ECDSA implementation for secp256k1 curve

Educational implementation showing the mathematical operations behind
elliptic curve cryptography used in Bitcoin.

WARNING: For educational purposes only. Not security audited.
Use standard libraries (ecdsa, cryptography) for production.
"""


class Point:
    """
    Represents a point on the elliptic curve.

    Special case: Point at infinity represented by x=None, y=None
    """

    def __init__(self, x, y):
        """
        Initialize a point on the curve.

        Args:
            x: x-coordinate (int or None for point at infinity)
            y: y-coordinate (int or None for point at infinity)
        """
        self.x = x
        self.y = y

    def is_infinity(self):
        """Check if this is the point at infinity."""
        return self.x is None and self.y is None

    def __eq__(self, other):
        """Check if two points are equal."""
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """String representation of the point."""
        if self.is_infinity():
            return "Point(infinity)"
        return f"Point(x={hex(self.x)[:20]}..., y={hex(self.y)[:20]}...)"


class Secp256k1:
    """
    secp256k1 elliptic curve parameters and operations.

    Curve equation: y² = x³ + 7 (mod p)
    """

    # Curve parameters
    # Prime field (2^256 - 2^32 - 977)
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    # Curve coefficient (y² = x³ + ax + b, for secp256k1: a=0, b=7)
    a = 0
    b = 7

    # Generator point G
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    # Order (number of points in the group)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    # Generator point
    G = Point(Gx, Gy)

    @staticmethod
    def mod_inverse(a, m):
        """
        Calculate modular inverse: a^(-1) mod m

        Uses Extended Euclidean Algorithm.
        Returns x where (a * x) ≡ 1 (mod m)

        Args:
            a: Number to invert
            m: Modulus

        Returns:
            Modular inverse of a mod m
        """
        if a < 0:
            a = a % m

        # Extended Euclidean Algorithm
        old_r, r = a, m
        old_s, s = 1, 0

        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s

        # old_r is gcd(a, m), should be 1 for inverse to exist
        if old_r != 1:
            raise ValueError(f"Modular inverse does not exist for {a} mod {m}")

        return old_s % m

    @classmethod
    def point_add(cls, P, Q):
        """
        Add two points on the curve: R = P + Q

        Args:
            P: First point
            Q: Second point

        Returns:
            Point representing P + Q
        """
        # Handle point at infinity
        if P.is_infinity():
            return Q
        if Q.is_infinity():
            return P

        # Handle point doubling (P == Q)
        if P == Q:
            return cls.point_double(P)

        # Handle inverse points (P.x == Q.x but P.y != Q.y)
        if P.x == Q.x:
            return Point(None, None)  # Point at infinity

        # Regular point addition
        # Step 1: Calculate slope s = (y2 - y1) / (x2 - x1) mod p
        numerator = (Q.y - P.y) % cls.p
        denominator = (Q.x - P.x) % cls.p
        denominator_inv = cls.mod_inverse(denominator, cls.p)
        s = (numerator * denominator_inv) % cls.p

        # Step 2: Calculate x3 = s² - x1 - x2 mod p
        x3 = (s * s - P.x - Q.x) % cls.p

        # Step 3: Calculate y3 = s(x1 - x3) - y1 mod p
        y3 = (s * (P.x - x3) - P.y) % cls.p

        return Point(x3, y3)

    @classmethod
    def point_double(cls, P):
        """
        Double a point on the curve: R = P + P

        Args:
            P: Point to double

        Returns:
            Point representing 2P
        """
        # Point at infinity
        if P.is_infinity():
            return P

        # If y = 0, result is point at infinity
        if P.y == 0:
            return Point(None, None)

        # Step 1: Calculate slope s = (3x₁²) / (2y₁) mod p
        # For secp256k1, a=0, so numerator is just 3x₁²
        numerator = (3 * P.x * P.x) % cls.p
        denominator = (2 * P.y) % cls.p
        denominator_inv = cls.mod_inverse(denominator, cls.p)
        s = (numerator * denominator_inv) % cls.p

        # Step 2: Calculate x3 = s² - 2x₁ mod p
        x3 = (s * s - 2 * P.x) % cls.p

        # Step 3: Calculate y3 = s(x₁ - x₃) - y₁ mod p
        y3 = (s * (P.x - x3) - P.y) % cls.p

        return Point(x3, y3)

    @classmethod
    def point_multiply(cls, k, P=None):
        """
        Multiply point by scalar: R = k × P

        Uses double-and-add algorithm for efficiency.

        Args:
            k: Scalar (private key)
            P: Point to multiply (defaults to generator G)

        Returns:
            Point representing k × P
        """
        if P is None:
            P = cls.G

        # Handle special cases
        if k == 0:
            return Point(None, None)  # Point at infinity
        if k == 1:
            return P

        # Normalize k to be positive
        k = k % cls.n

        # Double-and-add algorithm
        # Convert k to binary and process from left to right
        result = Point(None, None)  # Start with point at infinity
        addend = P

        # Process each bit of k from right to left
        while k > 0:
            if k & 1:  # If bit is 1
                result = cls.point_add(result, addend)
            addend = cls.point_double(addend)
            k >>= 1

        return result


class SigningKey:
    """
    ECDSA signing key (private key).

    Can generate signatures and derive verifying key (public key).
    """

    def __init__(self, private_key_bytes):
        """
        Initialize signing key from private key bytes.

        Args:
            private_key_bytes: 32 bytes representing the private key
        """
        if len(private_key_bytes) != 32:
            raise ValueError("Private key must be 32 bytes")

        # Convert bytes to integer
        self.private_key = int.from_bytes(private_key_bytes, byteorder='big')

        # Validate private key is in valid range [1, n-1]
        if not (1 <= self.private_key < Secp256k1.n):
            raise ValueError("Private key must be in range [1, n-1]")

    @classmethod
    def from_string(cls, private_key_bytes, curve=None):
        """
        Create SigningKey from bytes (compatible with ecdsa library API).

        Args:
            private_key_bytes: 32 bytes representing the private key
            curve: Curve object (ignored, always uses secp256k1)

        Returns:
            SigningKey instance
        """
        return cls(private_key_bytes)

    def get_verifying_key(self):
        """
        Derive the public key (verifying key) from private key.

        Returns:
            VerifyingKey instance
        """
        # Public key = private_key × G
        public_point = Secp256k1.point_multiply(self.private_key)
        return VerifyingKey(public_point)

    def to_string(self):
        """
        Export private key as bytes.

        Returns:
            32 bytes representing the private key
        """
        return self.private_key.to_bytes(32, byteorder='big')


class VerifyingKey:
    """
    ECDSA verifying key (public key).

    Can verify signatures.
    """

    def __init__(self, public_point):
        """
        Initialize verifying key from public point.

        Args:
            public_point: Point on the curve representing the public key
        """
        if public_point.is_infinity():
            raise ValueError("Public key cannot be point at infinity")

        self.public_point = public_point

    @classmethod
    def from_string(cls, public_key_bytes, curve=None):
        """
        Create VerifyingKey from bytes (compatible with ecdsa library API).

        Expects uncompressed public key (64 bytes: x + y coordinates).

        Args:
            public_key_bytes: 64 bytes (x + y coordinates, no prefix)
            curve: Curve object (ignored, always uses secp256k1)

        Returns:
            VerifyingKey instance
        """
        if len(public_key_bytes) != 64:
            raise ValueError("Public key must be 64 bytes (uncompressed, no prefix)")

        # Parse x and y coordinates
        x = int.from_bytes(public_key_bytes[:32], byteorder='big')
        y = int.from_bytes(public_key_bytes[32:], byteorder='big')

        # Verify point is on the curve
        # y² = x³ + 7 (mod p)
        left = (y * y) % Secp256k1.p
        right = (x * x * x + Secp256k1.b) % Secp256k1.p

        if left != right:
            raise ValueError("Point is not on the secp256k1 curve")

        return cls(Point(x, y))

    def to_string(self):
        """
        Export public key as bytes (uncompressed format, no prefix).

        Returns:
            64 bytes (x + y coordinates)
        """
        x_bytes = self.public_point.x.to_bytes(32, byteorder='big')
        y_bytes = self.public_point.y.to_bytes(32, byteorder='big')
        return x_bytes + y_bytes


# Curve constant for compatibility with ecdsa library
class SECP256k1:
    """Curve constant for API compatibility."""
    pass


def test_implementation():
    """
    Test the custom ECDSA implementation.
    """
    print("Testing custom ECDSA implementation (ecdsaRR)")
    print("=" * 60)

    # Test 1: Point doubling
    print("\nTest 1: Point Doubling")
    print(f"G = {Secp256k1.G}")
    G2 = Secp256k1.point_double(Secp256k1.G)
    print(f"2G = {G2}")

    # Test 2: Point addition
    print("\nTest 2: Point Addition")
    G3 = Secp256k1.point_add(Secp256k1.G, G2)
    print(f"G + 2G = 3G = {G3}")

    # Test 3: Point multiplication
    print("\nTest 3: Point Multiplication")
    k = 23
    kG = Secp256k1.point_multiply(k)
    print(f"{k}G = {kG}")

    # Test 4: Key generation
    print("\nTest 4: Key Generation")
    private_key_hex = "a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f"
    private_key_bytes = bytes.fromhex(private_key_hex)

    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()

    public_key_hex = vk.to_string().hex()
    print(f"Private key: {private_key_hex}")
    print(f"Public key:  04{public_key_hex}")

    # Verify against expected public key (from standard ecdsa library)
    print("\nTest 5: Verification against standard ecdsa library")
    try:
        import ecdsa as standard_ecdsa

        sk_standard = standard_ecdsa.SigningKey.from_string(
            private_key_bytes,
            curve=standard_ecdsa.SECP256k1
        )
        vk_standard = sk_standard.get_verifying_key()
        public_key_standard = vk_standard.to_string().hex()

        if public_key_hex == public_key_standard:
            print("[OK] Public keys match! Custom implementation is correct.")
        else:
            print("[FAIL] Public keys don't match!")
            print(f"  Custom:   {public_key_hex}")
            print(f"  Standard: {public_key_standard}")
    except ImportError:
        print("Standard ecdsa library not available for comparison")

    print("\n" + "=" * 60)
    print("Testing complete!")


if __name__ == "__main__":
    test_implementation()
