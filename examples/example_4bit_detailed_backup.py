"""
Example 4-bit ECDSA Operations

This file demonstrates the complete ECDSA workflow with a 4-bit implementation,
showing all intermediate values for educational purposes.

The small field size allows us to:
1. Enumerate all possible values
2. Visualize the discrete log problem
3. Understand why ECDSA is secure (it's hard to reverse even conceptually)
4. Test rollback approaches on a tractable problem
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.ecdsa4bit import (
    p, A, B, G, N, INFINITY,
    generate_keypair, sign, verify, point_multiply,
    point_add, generate_all_points, mod_inverse, is_on_curve
)


def trace_keypair_generation(private_key: int):
    """
    Trace through keypair generation step by step.
    Shows the discrete log problem in action.
    """
    print("\n" + "=" * 70)
    print("KEYPAIR GENERATION TRACE")
    print("=" * 70)
    print(f"\nCurve: y² = x³ + {A}x + {B} (mod {p})")
    print(f"Generator G = {G}")
    print(f"Order N = {N}")

    print(f"\nPrivate key d = {private_key}")
    print(f"  Binary: {bin(private_key)[2:].zfill(4)}")
    print(f"  This is our SECRET - we need to protect this!")

    print(f"\nComputing Public Key Q = d * G = {private_key} * {G}")
    print("Using double-and-add algorithm:")

    # Trace the double-and-add
    result = INFINITY
    addend = G
    k = private_key
    step = 0

    print(f"\n  Starting: result = O (infinity), addend = G = {G}")
    print(f"  k = {k} = {bin(k)[2:]}")

    temp_k = k
    while temp_k:
        bit = temp_k & 1
        step += 1
        print(f"\n  Step {step}:")
        print(f"    k = {temp_k}, LSB = {bit}")

        if bit:
            old_result = result
            result = point_add(result, addend)
            if old_result is None:
                print(f"    result = O + {addend} = {result}")
            else:
                print(f"    result = {old_result} + {addend} = {result}")

        old_addend = addend
        addend = point_add(addend, addend)
        print(f"    addend = 2 * {old_addend} = {addend}")

        temp_k >>= 1

    print(f"\nFinal Public Key Q = {result}")

    # Verify
    direct = point_multiply(private_key, G)
    print(f"Verification: {private_key} * G = {direct}")
    assert result == direct

    print("\n" + "-" * 70)
    print("THE DISCRETE LOG PROBLEM:")
    print("-" * 70)
    print(f"Given: G = {G}, Q = {result}")
    print(f"Find:  d such that Q = d * G")
    print(f"\nWith 4 bits, we can try all 15 values. In real ECDSA (256 bits),")
    print(f"there are 2^256 possibilities - computationally infeasible!")

    return private_key, result


def trace_signature_generation(private_key: int, public_key: tuple, message_hash: int, nonce: int):
    """
    Trace through signature generation step by step.
    Shows all intermediate values.
    """
    print("\n" + "=" * 70)
    print("SIGNATURE GENERATION TRACE")
    print("=" * 70)

    print(f"\nInputs:")
    print(f"  Private key d = {private_key}")
    print(f"  Public key Q = {public_key}")
    print(f"  Message hash z = {message_hash}")
    print(f"  Nonce k = {nonce} (THIS MUST BE SECRET AND RANDOM!)")

    # Step 1: Calculate R = k * G
    print(f"\nStep 1: Calculate R = k * G")
    R = point_multiply(nonce, G)
    print(f"  R = {nonce} * {G} = {R}")

    # Step 2: r = R.x mod N
    print(f"\nStep 2: r = R.x mod N")
    r = R[0] % N
    print(f"  r = {R[0]} mod {N} = {r}")

    # Step 3: Calculate s = k^(-1) * (z + r*d) mod N
    print(f"\nStep 3: Calculate s = k^(-1) * (z + r*d) mod N")

    k_inv = mod_inverse(nonce, N)
    print(f"  k^(-1) mod N = {k_inv}")
    print(f"  Verify: {nonce} * {k_inv} mod {N} = {(nonce * k_inv) % N}")

    inner = (message_hash + r * private_key) % N
    print(f"\n  z + r*d = {message_hash} + {r}*{private_key} = {message_hash + r * private_key}")
    print(f"  (z + r*d) mod N = {inner}")

    s = (k_inv * inner) % N
    print(f"\n  s = k^(-1) * (z + r*d) mod N")
    print(f"  s = {k_inv} * {inner} mod {N} = {s}")

    print(f"\nSignature: (r, s) = ({r}, {s})")

    # Show the relationship
    print("\n" + "-" * 70)
    print("KEY RELATIONSHIP (for rollback):")
    print("-" * 70)
    print(f"s = k^(-1) * (z + r*d) mod N")
    print(f"Therefore:")
    print(f"  s * k = z + r*d mod N")
    print(f"  r*d = s*k - z mod N")
    print(f"  d = r^(-1) * (s*k - z) mod N")
    print(f"\nIF we know k, we can recover d!")
    print(f"  r^(-1) mod N = {mod_inverse(r, N)}")
    print(f"  s*k - z = {s}*{nonce} - {message_hash} = {s*nonce - message_hash}")
    print(f"  (s*k - z) mod N = {(s*nonce - message_hash) % N}")
    d_recovered = (mod_inverse(r, N) * (s * nonce - message_hash)) % N
    print(f"  d = {mod_inverse(r, N)} * {(s*nonce - message_hash) % N} mod {N} = {d_recovered}")
    print(f"  Original d = {private_key}")
    print(f"  Match: {d_recovered == private_key}")

    return (r, s)


def trace_signature_verification(public_key: tuple, message_hash: int, signature: tuple):
    """
    Trace through signature verification step by step.
    """
    print("\n" + "=" * 70)
    print("SIGNATURE VERIFICATION TRACE")
    print("=" * 70)

    r, s = signature
    print(f"\nInputs:")
    print(f"  Public key Q = {public_key}")
    print(f"  Message hash z = {message_hash}")
    print(f"  Signature (r, s) = ({r}, {s})")

    # Step 1: w = s^(-1) mod N
    print(f"\nStep 1: w = s^(-1) mod N")
    w = mod_inverse(s, N)
    print(f"  w = {s}^(-1) mod {N} = {w}")

    # Step 2: u1 = z * w mod N
    print(f"\nStep 2: u1 = z * w mod N")
    u1 = (message_hash * w) % N
    print(f"  u1 = {message_hash} * {w} mod {N} = {u1}")

    # Step 3: u2 = r * w mod N
    print(f"\nStep 3: u2 = r * w mod N")
    u2 = (r * w) % N
    print(f"  u2 = {r} * {w} mod {N} = {u2}")

    # Step 4: Calculate point R' = u1*G + u2*Q
    print(f"\nStep 4: R' = u1*G + u2*Q")
    point1 = point_multiply(u1, G)
    print(f"  u1 * G = {u1} * {G} = {point1}")
    point2 = point_multiply(u2, public_key)
    print(f"  u2 * Q = {u2} * {public_key} = {point2}")
    R_prime = point_add(point1, point2)
    print(f"  R' = {point1} + {point2} = {R_prime}")

    # Step 5: Check R'.x mod N == r
    print(f"\nStep 5: Verify R'.x mod N == r")
    print(f"  R'.x mod N = {R_prime[0]} mod {N} = {R_prime[0] % N}")
    print(f"  r = {r}")
    valid = R_prime[0] % N == r
    print(f"  Match: {valid}")

    # Explain why this works
    print("\n" + "-" * 70)
    print("WHY VERIFICATION WORKS:")
    print("-" * 70)
    print("If signature is valid:")
    print("  s = k^(-1) * (z + r*d) mod N")
    print("  Therefore: k = s^(-1) * (z + r*d) mod N")
    print()
    print("  u1*G + u2*Q = z*w*G + r*w*Q")
    print("             = z*w*G + r*w*d*G")
    print("             = (z*w + r*w*d)*G")
    print("             = w*(z + r*d)*G")
    print("             = s^(-1)*(z + r*d)*G")
    print("             = k*G = R")
    print()
    print("So R'.x should equal R.x = r")

    return valid


def show_all_points_table():
    """Show a table of all points and their scalar multiples."""
    print("\n" + "=" * 70)
    print("COMPLETE POINT TABLE")
    print("=" * 70)

    points = generate_all_points()
    print(f"\nAll {len(points)} points on curve y² = x³ + {A}x + {B} (mod {p}):")

    # Print as table
    print("\n{:>4} | {:>10} | On Curve?".format("Idx", "Point"))
    print("-" * 30)
    for i, pt in enumerate(points):
        if pt is None:
            pt_str = "O (inf)"
        else:
            pt_str = f"({pt[0]:2d}, {pt[1]:2d})"
        on_curve = is_on_curve(pt)
        print(f"{i:4d} | {pt_str:>10} | {on_curve}")

    # Show scalar multiplication table for G
    print("\n" + "-" * 70)
    print("SCALAR MULTIPLICATION TABLE (k * G)")
    print("-" * 70)
    print("\n{:>4} | {:>10} | Binary k".format("k", "k * G"))
    print("-" * 35)
    for k in range(N + 1):
        kG = point_multiply(k, G)
        if kG is None:
            kG_str = "O (inf)"
        else:
            kG_str = f"({kG[0]:2d}, {kG[1]:2d})"
        print(f"{k:4d} | {kG_str:>10} | {bin(k)[2:].zfill(5)}")


def show_nonce_reuse_attack():
    """
    Demonstrate why nonce reuse is catastrophic in ECDSA.
    If the same k is used for two different messages, the private key is exposed!
    """
    print("\n" + "=" * 70)
    print("NONCE REUSE ATTACK DEMONSTRATION")
    print("=" * 70)
    print("\nThis shows why the nonce k MUST be unique for every signature!")

    private_key = 7
    _, public_key = generate_keypair(private_key)

    # Two different messages, SAME nonce (catastrophic!)
    z1 = 5   # First message hash
    z2 = 11  # Second message hash
    k = 3    # REUSED nonce - this is the vulnerability

    print(f"\nPrivate key (SECRET): d = {private_key}")
    print(f"Nonce (REUSED!): k = {k}")
    print(f"Message 1 hash: z1 = {z1}")
    print(f"Message 2 hash: z2 = {z2}")

    # Sign both messages with same k
    r, s1 = sign(private_key, z1, k)
    _, s2 = sign(private_key, z2, k)

    print(f"\nSignature 1: (r={r}, s1={s1})")
    print(f"Signature 2: (r={r}, s2={s2})")
    print(f"Notice: Both signatures have the SAME r value!")

    # Attack: recover k from the two signatures
    print("\n" + "-" * 70)
    print("ATTACK: Recovering k from two signatures with same r")
    print("-" * 70)

    print(f"\nFrom ECDSA signing:")
    print(f"  s1 = k^(-1) * (z1 + r*d) mod N")
    print(f"  s2 = k^(-1) * (z2 + r*d) mod N")

    print(f"\nSubtracting:")
    print(f"  s1 - s2 = k^(-1) * (z1 - z2) mod N")

    print(f"\nSolving for k:")
    print(f"  k = (z1 - z2) * (s1 - s2)^(-1) mod N")

    s_diff = (s1 - s2) % N
    z_diff = (z1 - z2) % N
    print(f"\n  z1 - z2 = {z1} - {z2} = {z1 - z2} = {z_diff} (mod {N})")
    print(f"  s1 - s2 = {s1} - {s2} = {s1 - s2} = {s_diff} (mod {N})")

    s_diff_inv = mod_inverse(s_diff, N)
    print(f"  (s1 - s2)^(-1) = {s_diff_inv}")

    k_recovered = (z_diff * s_diff_inv) % N
    print(f"\n  k = {z_diff} * {s_diff_inv} mod {N} = {k_recovered}")
    print(f"  Original k = {k}")
    print(f"  Match: {k_recovered == k}")

    # Now recover private key using k
    print("\n" + "-" * 70)
    print("ATTACK: Recovering private key d using k")
    print("-" * 70)

    print(f"\nFrom s1 = k^(-1) * (z1 + r*d) mod N:")
    print(f"  s1 * k = z1 + r*d mod N")
    print(f"  r*d = s1*k - z1 mod N")
    print(f"  d = r^(-1) * (s1*k - z1) mod N")

    r_inv = mod_inverse(r, N)
    d_recovered = (r_inv * (s1 * k_recovered - z1)) % N

    print(f"\n  r^(-1) = {r_inv}")
    print(f"  s1*k - z1 = {s1}*{k_recovered} - {z1} = {s1*k_recovered - z1} = {(s1*k_recovered - z1) % N} (mod {N})")
    print(f"  d = {r_inv} * {(s1*k_recovered - z1) % N} mod {N} = {d_recovered}")

    print(f"\nRecovered private key: d = {d_recovered}")
    print(f"Original private key:  d = {private_key}")
    print(f"ATTACK SUCCESSFUL: {d_recovered == private_key}")

    if d_recovered == private_key:
        print("\n*** PRIVATE KEY COMPLETELY COMPROMISED! ***")
        print("This is why nonce reuse in ECDSA is CATASTROPHIC.")
        print("Always use a cryptographically secure random nonce!")


def main():
    """Run all example demonstrations."""
    print("\n" + "=" * 70)
    print("4-BIT ECDSA EDUCATIONAL EXAMPLES")
    print("=" * 70)

    # Show point table
    show_all_points_table()

    # Trace keypair generation
    private_key, public_key = trace_keypair_generation(7)

    # Trace signature
    message_hash = 11
    nonce = 3
    signature = trace_signature_generation(private_key, public_key, message_hash, nonce)

    # Trace verification
    trace_signature_verification(public_key, message_hash, signature)

    # Show nonce reuse attack
    show_nonce_reuse_attack()

    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70)


if __name__ == "__main__":
    main()
