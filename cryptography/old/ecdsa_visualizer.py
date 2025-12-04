#!/usr/bin/env python3
"""
ECDSA Visualization and Step-by-Step Demonstration

This script demonstrates ECDSA (Elliptic Curve Digital Signature Algorithm)
with detailed step-by-step printing to visualize what's happening at each stage.

Uses the secp256k1 curve (used by Bitcoin) and the ecdsa library.

Online Resources for ECDSA Visualization:
- The Animated Elliptic Curve: https://curves.xargs.org/
- RareSkills ECDSA Tutorial: https://rareskills.io/post/ecdsa-tutorial
- Learn Me a Bitcoin ECDSA: https://learnmeabitcoin.com/technical/cryptography/elliptic-curve/ecdsa/
- Johannes Bauer ECC Tutorial: https://www.johannes-bauer.com/compsci/ecc/
"""

import hashlib
import secrets
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_string, sigdecode_string
from ecdsa.numbertheory import inverse_mod


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title):
    """Print a subsection header."""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def explain_modular_inverse():
    """Explain how modular inverse works and why it scrambles bits."""
    print_section("MODULAR INVERSE - THE KEY TO POINT OPERATIONS")

    print("""
WHAT IS MODULAR INVERSE?

    The modular inverse of 'a' mod 'p' is a number 'x' such that:
        a * x = 1 (mod p)

    Written as: x = a^(-1) mod p

    Example: inverse(3, 17) = 6
    Because: 3 * 6 = 18 = 1 (mod 17)


TWO FORMULAS FOR COMPUTING IT:

    1. Fermat's Little Theorem (only when p is prime):
       a^(-1) = a^(p-2) mod p

       Simple formula, but requires exponentiation (slow for big numbers).

    2. Extended Euclidean Algorithm (works for any coprime a, p):
       Find x, y such that: a*x + p*y = gcd(a, p) = 1
       Then: a^(-1) = x mod p

       This uses repeated division (fast, O(log p) steps).


STEP-BY-STEP EXAMPLE: inverse(3, 17)

    Using Extended Euclidean Algorithm:

    Step 1: 17 = 5*3 + 2    -->  2 = 17 - 5*3
    Step 2: 3 = 1*2 + 1     -->  1 = 3 - 1*2

    Back-substitute to express 1 in terms of 3 and 17:
        1 = 3 - 1*2
        1 = 3 - 1*(17 - 5*3)
        1 = 3 - 17 + 5*3
        1 = 6*3 - 17

    So: 6*3 = 1 (mod 17)
    Therefore: inverse(3, 17) = 6


WHY MODULAR INVERSE SCRAMBLES ALL BITS:

    The output depends on the ENTIRE GCD reduction sequence.
    Each step involves division and subtraction, mixing all bits.

    Example showing how bits get scrambled:
        inverse(2, 17) = 9     (because 2 * 9 = 18 = 1 mod 17)
        inverse(4, 17) = 13    (because 4 * 13 = 52 = 1 mod 17)
        inverse(8, 17) = 15    (because 8 * 15 = 120 = 1 mod 17)

    Notice: 2, 4, 8 have simple bit patterns (one bit set)
    But their inverses 9, 13, 15 have no obvious relationship!

    There is NO simple formula like "inverse(2a) = 2*inverse(a)".
    Each output bit depends on ALL input bits.


WHY THIS MATTERS FOR ECDSA SECURITY:

    Point addition and doubling formulas use modular inverse:

    Point doubling (2P):
        slope = (3*x^2 + a) * inverse(2*y, p)   <-- modular inverse!
        x_new = slope^2 - 2*x
        y_new = slope * (x - x_new) - y

    Point addition (P + Q):
        slope = (y2 - y1) * inverse(x2 - x1, p)  <-- modular inverse!
        x_new = slope^2 - x1 - x2
        y_new = slope * (x1 - x_new) - y1

    Because modular inverse scrambles all bits, there's NO correlation
    between the private key bits and the public key coordinate bits.

    Specifically: The LSB of Q.x does NOT tell you if private key d is even.
    If it did, you could recover d bit by bit in O(256) operations!
""")

    # Demonstrate with actual numbers
    print("-" * 80)
    print("  DEMONSTRATION: Computing inverses")
    print("-" * 80)

    p = 17
    print(f"\n  Using p = {p}")
    print(f"\n  {'a':>4} | {'inverse(a, p)':>14} | {'a * inverse':>12} | {'mod p':>6}")
    print(f"  {'-'*4}-+-{'-'*14}-+-{'-'*12}-+-{'-'*6}")

    for a in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
        inv = inverse_mod(a, p)
        product = a * inv
        print(f"  {a:>4} | {inv:>14} | {product:>12} | {product % p:>6}")

    print("\n  Notice: No simple pattern between a and inverse(a)!")


def visualize_curve_parameters():
    """Display the secp256k1 curve parameters."""
    print_section("SECP256K1 CURVE PARAMETERS")

    curve = SECP256k1.curve
    generator = SECP256k1.generator

    print("\nElliptic Curve Equation: y² = x³ + ax + b (mod p)")
    print(f"  a = {curve.a()}")
    print(f"  b = {curve.b()}")
    print(f"  p (prime) = {curve.p()}")
    print(f"    ({hex(curve.p())})")

    print("\nGenerator Point G:")
    print(f"  Gx = {generator.x()}")
    print(f"    ({hex(generator.x())})")
    print(f"  Gy = {generator.y()}")
    print(f"    ({hex(generator.y())})")

    print("\nCurve Order n (number of points):")
    print(f"  n = {SECP256k1.order}")
    print(f"    ({hex(SECP256k1.order)})")

    print("\nKey Facts:")
    print(f"  - Private key range: [1, n-1]")
    print(f"  - Public key = private_key * G (point multiplication)")
    print(f"  - Total possible private keys: ~2^256")
    print(f"  - Security level: ~128-bit")


def visualize_key_generation():
    """Generate and visualize ECDSA key pair."""
    print_section("STEP 1: KEY GENERATION")

    print("\n1.1 Generating Private Key...")
    print("  Method: Generate random number in range [1, n-1]")

    # Generate private key
    sk = SigningKey.generate(curve=SECP256k1)
    private_key_int = sk.privkey.secret_multiplier

    print(f"\n  Private Key (d):")
    print(f"    Decimal: {private_key_int}")
    print(f"    Hex:     {hex(private_key_int)}")
    print(f"    Bytes:   {private_key_int.to_bytes(32, 'big').hex()}")
    print(f"    Length:  {private_key_int.bit_length()} bits")

    print("\n1.2 Computing Public Key...")
    print("  Formula: Q = d * G")
    print("  Where:")
    print("    d = private key (scalar - just a number)")
    print("    G = generator point (fixed starting point on the curve)")
    print("    Q = public key point (your unique point on the curve)")
    print("    * = elliptic curve point multiplication")

    print("\n  What are X and Y?")
    print("    - The elliptic curve is a 2D graph")
    print("    - Every point on it has coordinates (x, y)")
    print("    - Generator point G has coordinates (Gx, Gy)")
    print("    - Your public key Q has coordinates (Qx, Qy)")
    print("    - These points satisfy: y² = x³ + 7 (mod p)")

    vk = sk.get_verifying_key()
    public_key_point = vk.pubkey.point

    generator = SECP256k1.generator

    print(f"\n  Starting Point (Generator G):")
    print(f"    Gx = {generator.x()}")
    print(f"    Gy = {generator.y()}")

    print(f"\n  Your Public Key Point Q = d × G = (Qx, Qy):")
    print(f"    Qx = {public_key_point.x()}")
    print(f"      ({hex(public_key_point.x())})")
    print(f"    Qy = {public_key_point.y()}")
    print(f"      ({hex(public_key_point.y())})")

    print(f"\n  How are Qx and Qy calculated?")
    print(f"    - Start with generator point G = (Gx, Gy)")
    print(f"    - Multiply it by your private key d = {private_key_int}")
    print(f"    - Point multiplication: Add G to itself d times (optimized)")
    print(f"    - Result is a new point Q = (Qx, Qy) on the curve")
    print(f"    - This is a ONE-WAY function:")
    print(f"        Easy: d and G -> compute Q")
    print(f"        Hard: Q and G -> find d (Elliptic Curve Discrete Log Problem)")

    # Verify point is on curve
    curve = SECP256k1.curve
    y_squared = (public_key_point.y() ** 2) % curve.p()
    x_cubed_plus_b = (public_key_point.x() ** 3 + curve.b()) % curve.p()

    print(f"\n  Verification: Point Q is on curve?")
    print(f"    y² mod p = {y_squared}")
    print(f"    x³ + b mod p = {x_cubed_plus_b}")
    if y_squared == x_cubed_plus_b:
        print(f"    Match: True [OK]")
    else:
        print(f"    Match: False [FAIL]")

    # Compressed vs Uncompressed
    print(f"\n  Public Key Formats:")
    print(f"    Uncompressed (65 bytes): 04 || Qx || Qy")
    print(f"      {vk.to_string('uncompressed').hex()}")
    print(f"    Compressed (33 bytes): 02/03 || Qx")
    print(f"      {vk.to_string('compressed').hex()}")
    print(f"      (02 if Qy even, 03 if Qy odd)")

    return sk, vk


def visualize_point_operations():
    """Demonstrate how point addition and doubling work to calculate x,y coordinates."""
    print_section("HOW X AND Y ARE CALCULATED: POINT OPERATIONS")

    curve = SECP256k1.curve
    G = SECP256k1.generator
    n = SECP256k1.order

    print("\nElliptic Curve Point Multiplication: Q = d * G")
    print("  This doesn't mean regular multiplication!")
    print("  It means: G + G + G + ... (d times)")
    print("  But we use optimizations (double-and-add algorithm)")

    print("\n" + "-" * 80)
    print("POINT DOUBLING: How to calculate 2P = P + P")
    print("-" * 80)

    # Demonstrate point doubling with G
    print(f"\nExample: Calculate 2G (G + G)")
    print(f"\n  Input Point G:")
    print(f"    Gx = {G.x()}")
    print(f"    Gy = {G.y()}")

    # Calculate 2G
    G2 = G + G  # Point doubling

    print(f"\n  Point Doubling Formula (when x1 = x2):")
    print(f"    lambda = (3*x1^2 + a) / (2*y1) mod p")
    print(f"    x3 = lambda^2 - 2*x1 mod p")
    print(f"    y3 = lambda*(x1 - x3) - y1 mod p")

    # Calculate slope lambda manually
    a = curve.a()
    p = curve.p()
    x1, y1 = G.x(), G.y()

    # lambda = (3*x1^2 + a) / (2*y1) mod p
    numerator = (3 * x1 * x1 + a) % p
    denominator = (2 * y1) % p
    # Modular inverse of denominator
    from ecdsa.numbertheory import inverse_mod
    denom_inv = inverse_mod(denominator, p)
    slope = (numerator * denom_inv) % p

    # Calculate new point
    x3 = (slope * slope - 2 * x1) % p
    y3 = (slope * (x1 - x3) - y1) % p

    print(f"\n  Step-by-step calculation:")
    print(f"    a = {a}")
    print(f"    p = {hex(p)}")
    print(f"    numerator = 3*{x1}^2 + {a} mod p")
    print(f"    denominator = 2*{y1} mod p")
    print(f"    lambda = {hex(slope)}")
    print(f"\n    x3 = lambda^2 - 2*x1 mod p")
    print(f"       = {hex(x3)}")
    print(f"    y3 = lambda*(x1 - x3) - y1 mod p")
    print(f"       = {hex(y3)}")

    print(f"\n  Result 2G = (x3, y3):")
    print(f"    x3 = {G2.x()}")
    print(f"    y3 = {G2.y()}")
    print(f"\n  Verification: Calculated matches library? {x3 == G2.x() and y3 == G2.y()} [OK]")

    print("\n" + "-" * 80)
    print("POINT ADDITION: How to calculate P + Q (different points)")
    print("-" * 80)

    print(f"\nExample: Calculate 3G = 2G + G")

    # Calculate 3G
    G3 = G2 + G

    print(f"\n  Input Points:")
    print(f"    P = 2G: ({G2.x()}, {G2.y()})")
    print(f"    Q = G:  ({G.x()}, {G.y()})")

    print(f"\n  Point Addition Formula (when x1 != x2):")
    print(f"    lambda = (y2 - y1) / (x2 - x1) mod p")
    print(f"    x3 = lambda^2 - x1 - x2 mod p")
    print(f"    y3 = lambda*(x1 - x3) - y1 mod p")

    # Calculate manually
    x1, y1 = G2.x(), G2.y()
    x2, y2 = G.x(), G.y()

    numerator = (y2 - y1) % p
    denominator = (x2 - x1) % p
    denom_inv = inverse_mod(denominator, p)
    slope = (numerator * denom_inv) % p

    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p

    print(f"\n  Result 3G:")
    print(f"    x3 = {G3.x()}")
    print(f"    y3 = {G3.y()}")
    print(f"\n  Verification: Calculated matches library? {x3 == G3.x() and y3 == G3.y()} [OK]")

    print("\n" + "-" * 80)
    print("DOUBLE-AND-ADD ALGORITHM: Efficient Multiplication")
    print("-" * 80)

    print("\n  To calculate d * G efficiently:")
    print("  1. Convert d to binary")
    print("  2. For each bit (from left to right):")
    print("     - Double the current point")
    print("     - If bit is 1, add G")

    print("\n  Example: Calculate 7G (7 in binary = 111)")
    print("    Binary: 1  1  1")
    print("    Step 0: R = G        (first bit is always 1)")
    print("    Step 1: R = 2R = 2G  (double)")
    print("            R = R+G = 3G (bit is 1, so add G)")
    print("    Step 2: R = 2R = 6G  (double)")
    print("            R = R+G = 7G (bit is 1, so add G)")

    # Verify
    G7 = 7 * G
    print(f"\n  Result 7G:")
    print(f"    x = {G7.x()}")
    print(f"    y = {G7.y()}")

    print("\n  For large d (256-bit private key):")
    print("    - Requires only ~256 doublings and ~128 additions (on average)")
    print("    - Much faster than adding G to itself d times!")
    print("    - This is why d × G is fast, but reversing it is hard")


def visualize_message_hash(message):
    """Hash a message and show the process."""
    print_section("STEP 2: MESSAGE HASHING")

    print(f"\n2.1 Original Message:")
    print(f"  Message: '{message}'")
    print(f"  Bytes:   {message.encode().hex()}")
    print(f"  Length:  {len(message)} characters, {len(message.encode())} bytes")

    print(f"\n2.2 Hashing with SHA-256...")
    print(f"  SHA-256 is a cryptographic hash function:")
    print(f"    - Input: any length")
    print(f"    - Output: 256 bits (32 bytes)")
    print(f"    - Properties: one-way, collision-resistant, deterministic")

    message_hash = hashlib.sha256(message.encode()).digest()
    hash_int = int.from_bytes(message_hash, 'big')

    print(f"\n  Message Hash (e):")
    print(f"    Hex:     {message_hash.hex()}")
    print(f"    Decimal: {hash_int}")
    print(f"    Length:  256 bits")

    print(f"\n  Note: This hash will be signed, not the original message")

    return message_hash, hash_int


def visualize_signature_generation(sk, message_hash):
    """Generate and visualize ECDSA signature."""
    print_section("STEP 3: SIGNATURE GENERATION")

    private_key = sk.privkey.secret_multiplier
    n = SECP256k1.order

    print("\n3.1 Generate Random Nonce k...")
    print("  CRITICAL: k must be:")
    print("    - Random and unpredictable")
    print("    - Different for each signature")
    print("    - Never reused (reuse allows private key recovery!)")
    print("    - In range [1, n-1]")

    # Generate nonce (the library does this internally, we'll simulate)
    k = secrets.randbelow(n - 1) + 1

    print(f"\n  Nonce k:")
    print(f"    Decimal: {k}")
    print(f"    Hex:     {hex(k)}")
    print(f"    Length:  {k.bit_length()} bits")

    print("\n3.2 Calculate Point R = k * G...")
    print("  Where:")
    print("    k = nonce")
    print("    G = generator point")
    print("    R = (Rx, Ry)")

    # Calculate R = k * G
    R = k * SECP256k1.generator

    print(f"\n  Point R:")
    print(f"    Rx = {R.x()}")
    print(f"      ({hex(R.x())})")
    print(f"    Ry = {R.y()}")
    print(f"      ({hex(R.y())})")

    print("\n3.3 Calculate r = Rx mod n...")
    r = R.x() % n

    print(f"\n  Signature component r:")
    print(f"    r = {r}")
    print(f"    ({hex(r)})")

    print("\n  Check: r != 0?")
    if r != 0:
        print(f"    True [OK]")
    else:
        print(f"    False [FAIL] (must regenerate k)")

    print("\n3.4 Calculate s = k^-1(e + d*r) mod n...")
    print("  Where:")
    print("    k^-1 = modular inverse of k")
    print("    e = message hash (as integer)")
    print("    d = private key")
    print("    r = first signature component")
    print("    n = curve order")

    e = int.from_bytes(message_hash, 'big')
    k_inv = inverse_mod(k, n)

    print(f"\n  Calculating k^-1 (modular inverse of k):")
    print(f"    k * k^-1 = 1 (mod n)")
    print(f"    k^-1 = {k_inv}")
    print(f"    Verify: (k * k^-1) mod n = {(k * k_inv) % n} [OK]")

    print(f"\n  Calculating s:")
    print(f"    e + d*r = {e} + {private_key}*{r}")
    print(f"            = {(e + private_key * r) % n}")
    print(f"    s = k^-1 * (e + d*r) mod n")

    s = (k_inv * (e + private_key * r)) % n

    print(f"    s = {s}")
    print(f"      ({hex(s)})")

    print("\n  Check: s != 0?")
    if s != 0:
        print(f"    True [OK]")
    else:
        print(f"    False [FAIL] (must regenerate k)")

    # Actually sign with the library for comparison
    actual_sig = sk.sign_digest(message_hash, sigencode=sigencode_string)
    r_actual = int.from_bytes(actual_sig[:32], 'big')
    s_actual = int.from_bytes(actual_sig[32:], 'big')

    print("\n3.5 Final Signature:")
    print(f"  Signature = (r, s)")
    print(f"    r = {r_actual}")
    print(f"    s = {s_actual}")
    print(f"\n  DER Encoding (used in Bitcoin):")
    print(f"    {actual_sig.hex()}")
    print(f"    Length: {len(actual_sig)} bytes")

    print("\n  Signature Components (32 bytes each):")
    print(f"    r (hex): {r_actual.to_bytes(32, 'big').hex()}")
    print(f"    s (hex): {s_actual.to_bytes(32, 'big').hex()}")

    return actual_sig, (r_actual, s_actual)


def visualize_signature_verification(vk, message_hash, signature, r_s_tuple):
    """Verify and visualize ECDSA signature verification."""
    print_section("STEP 4: SIGNATURE VERIFICATION")

    r, s = r_s_tuple
    e = int.from_bytes(message_hash, 'big')
    n = SECP256k1.order

    print("\n4.1 Extract Signature Components...")
    print(f"  r = {r}")
    print(f"  s = {s}")

    print("\n4.2 Verify r and s are in valid range...")
    print(f"  Check: 1 <= r < n?  {1 <= r < n} [OK]" if 1 <= r < n else f"  Check: 1 <= r < n?  False [FAIL]")
    print(f"  Check: 1 <= s < n?  {1 <= s < n} [OK]" if 1 <= s < n else f"  Check: 1 <= s < n?  False [FAIL]")

    print("\n4.3 Calculate w = s^-1 mod n...")
    print("  w is the modular inverse of s")

    w = inverse_mod(s, n)

    print(f"  w = {w}")
    print(f"    ({hex(w)})")
    print(f"  Verify: (s * w) mod n = {(s * w) % n} [OK]")

    print("\n4.4 Calculate u1 = e * w mod n...")
    print(f"  Where e = message hash")

    u1 = (e * w) % n

    print(f"  u1 = {u1}")
    print(f"    ({hex(u1)})")

    print("\n4.5 Calculate u2 = r * w mod n...")

    u2 = (r * w) % n

    print(f"  u2 = {u2}")
    print(f"    ({hex(u2)})")

    print("\n4.6 Calculate Point P = u1*G + u2*Q...")
    print("  Where:")
    print("    G = generator point")
    print("    Q = public key point")
    print("    P = verification point")
    print("\n  This is the KEY step:")
    print("    - If signature is valid, P.x mod n will equal r")
    print("    - This works because of elliptic curve math properties")

    G = SECP256k1.generator
    Q = vk.pubkey.point

    # Calculate P = u1*G + u2*Q
    P = u1 * G + u2 * Q

    print(f"\n  Point P = (Px, Py):")
    print(f"    Px = {P.x()}")
    print(f"      ({hex(P.x())})")
    print(f"    Py = {P.y()}")
    print(f"      ({hex(P.y())})")

    print("\n4.7 Calculate v = Px mod n...")

    v = P.x() % n

    print(f"  v = {v}")
    print(f"    ({hex(v)})")

    print("\n4.8 Final Verification: v == r?")
    print(f"  v = {v}")
    print(f"  r = {r}")
    print(f"\n  Match: {v == r}")

    if v == r:
        print("\n  [OK] SIGNATURE VALID!")
        print("    - The signature was created by the private key holder")
        print("    - The message has not been tampered with")
        print("    - The signature is authentic")
    else:
        print("\n  [FAIL] SIGNATURE INVALID!")
        print("    - Either the signature is forged")
        print("    - Or the message was modified")
        print("    - Or the wrong public key was used")

    # Verify with library
    print("\n4.9 Library Verification...")
    try:
        vk.verify_digest(signature, message_hash, sigdecode=sigdecode_string)
        print("  ecdsa library verification: VALID [OK]")
    except:
        print("  ecdsa library verification: INVALID [FAIL]")


def demonstrate_why_ecdsa_works():
    """Explain the mathematics behind why ECDSA works."""
    print_section("WHY ECDSA WORKS - THE MATHEMATICS")

    print("\nKey Mathematical Properties:")

    print("\n1. Elliptic Curve Point Multiplication:")
    print("   - Given point P and scalar k, we can compute k*P efficiently")
    print("   - But given P and k*P, finding k is extremely hard (ECDLP)")
    print("   - This is the 'discrete logarithm problem' for elliptic curves")

    print("\n2. Signature Generation Creates a Mathematical Relationship:")
    print("   s = k^-1(e + d*r) mod n")
    print("   Rearranging: k*s = e + d*r mod n")
    print("                k*s - d*r = e mod n")

    print("\n3. Verification Reconstructs the Same Point:")
    print("   P = u1*G + u2*Q")
    print("   Substituting u1 = e*w, u2 = r*w, w = s^-1:")
    print("   P = (e*s^-1)*G + (r*s^-1)*Q")
    print("   P = (e*s^-1)*G + (r*s^-1)*(d*G)")  # Q = d*G
    print("   P = s^-1(e*G + r*d*G)")
    print("   P = s^-1(e + r*d)*G")

    print("\n4. From Signing: s = k^-1(e + d*r), so k = s^-1(e + d*r)")
    print("   Therefore: P = k*G = R")
    print("   And: Px mod n = Rx mod n = r  [OK]")

    print("\n5. Security Guarantees:")
    print("   - Private key (d) never revealed")
    print("   - Nonce (k) never revealed")
    print("   - Only r (Rx mod n) and s are public")
    print("   - Cannot derive d or k from (r, s) due to ECDLP hardness")
    print("   - If k is reused, private key CAN be recovered!")

    print("\n6. Why This Matters for Bitcoin:")
    print("   - Proves you own the private key without revealing it")
    print("   - Anyone can verify signature with just public key")
    print("   - Signatures are unique to each transaction (different k)")
    print("   - 256-bit security level (infeasible to break)")


def demonstrate_nonce_reuse_vulnerability():
    """Show why reusing nonce k is catastrophic."""
    print_section("SECURITY: NONCE REUSE VULNERABILITY")

    print("\nWARNING: Never reuse nonce k!")
    print("\nIf the same k is used for two different messages:")

    print("\nSignature 1: s1 = k^-1(e1 + d*r) mod n")
    print("Signature 2: s2 = k^-1(e2 + d*r) mod n")
    print("\nSubtracting:")
    print("s1 - s2 = k^-1(e1 - e2) mod n")
    print("\nSolving for k:")
    print("k = (e1 - e2) / (s1 - s2) mod n")
    print("\nOnce k is known, the private key can be recovered:")
    print("d = r^-1(k*s1 - e1) mod n")

    print("\n[!] This is how Sony's PS3 private key was recovered in 2010!")
    print("    They used the same k for multiple signatures.")

    print("\n[!] Modern libraries use deterministic k generation (RFC 6979)")
    print("    k = HMAC-SHA256(private_key, message_hash)")
    print("    This ensures k is unique but deterministic.")


def main():
    """Run complete ECDSA visualization."""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#  ECDSA (Elliptic Curve Digital Signature Algorithm) Visualization" + " " * 10 + "#")
    print("#  Using secp256k1 (Bitcoin's curve)" + " " * 45 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    # Step 0: Curve parameters
    visualize_curve_parameters()

    # Step 0.5: Modular inverse (key to understanding point operations)
    explain_modular_inverse()

    # Step 1: Key generation
    signing_key, verifying_key = visualize_key_generation()

    # Step 1.5: Point operations (how x,y are calculated)
    visualize_point_operations()

    # Step 2: Message hashing
    message = "Hello, Bitcoin!"
    message_hash, hash_int = visualize_message_hash(message)

    # Step 3: Signature generation
    signature, r_s = visualize_signature_generation(signing_key, message_hash)

    # Step 4: Signature verification
    visualize_signature_verification(verifying_key, message_hash, signature, r_s)

    # Additional explanations
    demonstrate_why_ecdsa_works()
    demonstrate_nonce_reuse_vulnerability()

    # Summary
    print_section("SUMMARY")
    print("\nECDSA Process:")
    print("  1. Generate private key d (random number)")
    print("  2. Calculate public key Q = d * G (point multiplication)")
    print("  3. Hash message to get e")
    print("  4. Generate random nonce k")
    print("  5. Calculate R = k * G")
    print("  6. Calculate r = Rx mod n")
    print("  7. Calculate s = k^-1(e + d*r) mod n")
    print("  8. Signature = (r, s)")
    print("\nVerification:")
    print("  1. Calculate w = s^-1 mod n")
    print("  2. Calculate u1 = e*w mod n")
    print("  3. Calculate u2 = r*w mod n")
    print("  4. Calculate P = u1*G + u2*Q")
    print("  5. Verify Px mod n == r")

    print("\nKey Takeaways:")
    print("  [OK] ECDSA provides authentication without revealing private key")
    print("  [OK] Based on hardness of elliptic curve discrete log problem")
    print("  [OK] Used in Bitcoin, Ethereum, TLS, and many other systems")
    print("  [OK] Nonce k MUST be unique for each signature")
    print("  [OK] Modern implementations use deterministic k (RFC 6979)")

    print("\n" + "#" * 80)
    print("#  Visualization Complete!" + " " * 56 + "#")
    print("#" * 80)
    print()


if __name__ == '__main__':
    main()
