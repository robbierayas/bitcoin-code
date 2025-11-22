"""
RIPEMD-160 Hash Algorithm Implementation

This is a clean, working implementation of the RIPEMD-160 cryptographic hash function.
RIPEMD-160 produces a 160-bit (20-byte) hash value from arbitrary input data.

Used in Bitcoin for generating addresses from public keys.

Reference: https://homes.esat.kuleuven.be/~bosselae/ripemd160.html
"""

import os
import math


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def makehex(value, size=8):
    """Convert integer to hex string with specified size.

    Args:
        value: Integer value to convert
        size: Desired string length (default 8)

    Returns:
        Hex string padded with leading zeros
    """
    value = hex(value)[2:]
    if value[-1] == 'L':
        value = value[0:-1]
    while len(value) < size:
        value = '0' + value
    return value


def makebin(value, size=32):
    """Convert integer to binary string with specified size.

    Args:
        value: Integer value to convert
        size: Desired string length (default 32)

    Returns:
        Binary string padded with leading zeros
    """
    value = bin(value)[2:]
    while len(value) < size:
        value = '0' + value
    return value


def ROL(value, n):
    """Rotate Left operation - circular left shift.

    Args:
        value: 32-bit integer value
        n: Number of bits to rotate

    Returns:
        Rotated 32-bit value
    """
    return (value << n) | (value >> (32 - n))


def little_end(string, base=16):
    """Convert string to little-endian format.

    Args:
        string: Input string (hex or binary)
        base: 16 for hex, 2 for binary

    Returns:
        String in little-endian byte order
    """
    t = ''
    if base == 2:
        s = 8
    if base == 16:
        s = 2
    for x in range(len(string) // s):
        t = string[s*x:s*(x+1)] + t
    return t


# ============================================================================
# RIPEMD-160 ALGORITHM
# ============================================================================

def F(x, y, z, round):
    """RIPEMD-160 mixing function - varies by round number.

    Five different boolean functions are used across 80 rounds:
    - Rounds 0-15:   f(x,y,z) = x XOR y XOR z
    - Rounds 16-31:  f(x,y,z) = (x AND y) OR (NOT x AND z)
    - Rounds 32-47:  f(x,y,z) = (x OR NOT y) XOR z
    - Rounds 48-63:  f(x,y,z) = (x AND z) OR (y AND NOT z)
    - Rounds 64-79:  f(x,y,z) = x XOR (y OR NOT z)

    Args:
        x, y, z: 32-bit integer values
        round: Current round number (0-79)

    Returns:
        Result of mixing function
    """
    if round < 16:
        return x ^ y ^ z
    elif 16 <= round < 32:
        return (x & y) | (~x & z)
    elif 32 <= round < 48:
        return (x | ~y) ^ z
    elif 48 <= round < 64:
        return (x & z) | (y & ~z)
    elif 64 <= round:
        return x ^ (y | ~z)


def RIPEMD160(data):
    """Compute RIPEMD-160 hash of hex input data.

    RIPEMD-160 is a 160-bit cryptographic hash function designed as a
    strengthened version of RIPEMD. It processes data in 512-bit blocks
    using two parallel lines of computation (left and right) with 80 rounds each.

    Args:
        data: Input data as hexadecimal string

    Returns:
        160-bit hash as 40-character hexadecimal string

    Example:
        >>> RIPEMD160('')
        '9c1185a5c5e9fc54612808977ee8f548b2258d31'

        >>> RIPEMD160('61')  # Hash of 'a'
        '0bdc9d2d256b3ee9daae347be6f4dc835a467ffe'
    """

    # RIPEMD-160 initial hash values (160 bits = 5 x 32-bit words)
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    # Left line round constants (5 rounds of 16 steps each)
    k = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]

    # Right line round constants (parallel computation)
    kk = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000]

    # Left line rotation amounts per round (80 values)
    s = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
         7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
         11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
         11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
         9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]

    # Right line rotation amounts per round (80 values)
    ss = [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
          9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
          9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
          15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
          8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]

    # Left line message word selection order (80 values)
    r = list(range(16)) + [7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
                           3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
                           1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
                           4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]

    # Right line message word selection order (80 values)
    rr = [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
          6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
          15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
          8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
          12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]

    # ========================================================================
    # PREPROCESSING - Padding and length encoding
    # ========================================================================

    # Convert hex data to binary
    temp = ''
    for x in data:
        temp += makebin(int(x, 16), 4)

    length = len(temp) % 2**64

    # Append '1' bit followed by zeros until length ≡ 448 (mod 512)
    temp += '1'
    while len(temp) % 512 != 448:
        temp += '0'

    # Append 64-bit length in little-endian format
    input_data = temp
    temp = makebin(length, 64)
    bit_length = ''
    for x in range(len(input_data) // 32):
        bit_length += little_end(temp[32*x:32*(x+1)], 2)
    input_data += bit_length[32:] + bit_length[:32]

    # Number of 512-bit blocks to process
    num_blocks = len(input_data) // 512

    # ========================================================================
    # MAIN HASH COMPUTATION - Process each 512-bit block
    # ========================================================================

    for i in range(num_blocks):
        # Initialize working variables for left and right lines
        # (aa, bb, cc, dd, ee) are parallel to (a, b, c, d, e)
        a = aa = h0
        b = bb = h1
        c = cc = h2
        d = dd = h3
        e = ee = h4

        # Break block into 16 x 32-bit words
        X = input_data[512*i:512*(i+1)]
        X = [int(little_end(X[32*x:32*(x+1)], 2), 2) for x in range(16)]

        # 80 rounds of hashing (split into left and right parallel lines)
        for j in range(80):
            # LEFT LINE
            T = (ROL((a + F(b, c, d, j) + X[r[j]] + k[j//16]) % 2**32, s[j]) + e) % 2**32
            c = ROL(c, 10) % 2**32
            a = e
            e = d
            d = c
            c = b
            b = T

            # RIGHT LINE (uses reversed round order: 79-j)
            T = (ROL((aa + F(bb, cc, dd, 79-j) + X[rr[j]] + kk[j//16]) % 2**32, ss[j]) + ee) % 2**32
            cc = ROL(cc, 10) % 2**32
            aa = ee
            ee = dd
            dd = cc
            cc = bb
            bb = T

        # Update hash values (combine left and right lines)
        T = (h1 + c + dd) % 2**32
        h1 = (h2 + d + ee) % 2**32
        h2 = (h3 + e + aa) % 2**32
        h3 = (h4 + a + bb) % 2**32
        h4 = (h0 + b + cc) % 2**32
        h0 = T

    # ========================================================================
    # OUTPUT - Combine final hash values in little-endian format
    # ========================================================================

    result = (little_end(makehex(h0)) +
              little_end(makehex(h1)) +
              little_end(makehex(h2)) +
              little_end(makehex(h3)) +
              little_end(makehex(h4)))

    return result