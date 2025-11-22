# RIPEMD-160 Algorithm Reference

Complete technical reference for the RIPEMD-160 cryptographic hash function.

## Table of Contents

1. [Overview](#overview)
2. [Algorithm Structure](#algorithm-structure)
3. [Step-by-Step Process](#step-by-step-process)
4. [Mathematical Operations](#mathematical-operations)
5. [Constants and Tables](#constants-and-tables)
6. [Bitcoin Usage](#bitcoin-usage)
7. [Implementation Details](#implementation-details)
8. [Test Vectors](#test-vectors)
9. [Security Considerations](#security-considerations)

---

## Overview

### What is RIPEMD-160?

**RIPEMD-160** (RACE Integrity Primitives Evaluation Message Digest, 160-bit) is a cryptographic hash function that produces a 160-bit (20-byte) hash value from arbitrary input data.

**Key Properties:**
- **Input:** Any length of data
- **Output:** 160-bit (20-byte) hash value
- **Block Size:** 512 bits (64 bytes)
- **Design:** Two parallel lines of computation
- **Rounds:** 80 rounds total (5 blocks × 16 rounds each)

**Creator:** Hans Dobbertin, Antoon Bosselaers, and Bart Preneel (1996)

**Purpose:**
- Strengthened version of RIPEMD
- Alternative to SHA-1
- Used extensively in Bitcoin for address generation

---

## Algorithm Structure

### High-Level Overview

```
Input Message
    ↓
[1] Preprocessing (Padding)
    ↓
[2] Initialize Hash Values (h0-h4)
    ↓
[3] Process 512-bit Blocks
    ├─ Left Line (80 rounds)
    └─ Right Line (80 rounds, parallel)
    ↓
[4] Finalize (Combine results)
    ↓
160-bit Hash Output
```

### Dual-Line Architecture

RIPEMD-160 uses **two parallel computation lines**:

```
                    Input Block (512 bits)
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
         LEFT LINE                 RIGHT LINE
      (rounds 0-79)              (rounds 79-0)
      uses K[0-4]                uses K'[0-4]
      uses s[0-79]               uses s'[0-79]
      uses r[0-79]               uses r'[0-79]
              ↓                         ↓
              └────────────┬────────────┘
                           ↓
                    Combine Results
                           ↓
                    Final Hash (160 bits)
```

**Why Two Lines?**
- Increases security against cryptanalysis
- Makes differential attacks harder
- Provides redundancy in computation

---

## Step-by-Step Process

### Step 1: Preprocessing (Padding)

#### Goal
Ensure message length is congruent to 448 modulo 512.

#### Process

1. **Append '1' bit** to the message
2. **Append '0' bits** until length ≡ 448 (mod 512)
3. **Append 64-bit length** (message length in bits, little-endian)

#### Example

```
Original message (in bits): 01100001  (1 byte = 'a')
                           ↓
After '1' bit:             01100001 1
                           ↓
After '0' padding:         01100001 10000000 00000000 ... (to 448 bits)
                           ↓
After length (64 bits):    ... 00001000 00000000 ... (length = 8)
                           ↓
Total: 512 bits (1 block)
```

#### Padding Formula

```
Padded Length = Original Length + 1 + k + 64
where k = smallest number such that (Original Length + 1 + k) ≡ 448 (mod 512)
```

### Step 2: Initialize Hash Values

Five 32-bit words (h0, h1, h2, h3, h4) are initialized:

```
h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0
```

These are the same initial values as RIPEMD-128 and MD4/MD5 (first 4 values).

### Step 3: Process Each 512-bit Block

For each 512-bit block of the padded message:

#### 3.1 Divide into 16 Words

Break the 512-bit block into sixteen 32-bit words (X[0] through X[15]):

```
512 bits = 16 words × 32 bits/word
```

Words are in **little-endian** format.

#### 3.2 Initialize Working Variables

```
A  = h0    Ar = h0
B  = h1    Br = h1
C  = h2    Cr = h2
D  = h3    Dr = h3
E  = h4    Er = h4
```

Left line uses (A, B, C, D, E)
Right line uses (Ar, Br, Cr, Dr, Er)

#### 3.3 Perform 80 Rounds

**For j = 0 to 79:**

##### Left Line Operation

```
T = ROL(A + f(j, B, C, D) + X[r[j]] + K[j/16], s[j]) + E
A = E
E = D
D = C
C = ROL(B, 10)
B = T
```

##### Right Line Operation (Parallel)

```
T = ROL(Ar + f(79-j, Br, Cr, Dr) + X[r'[j]] + K'[j/16], s'[j]) + Er
Ar = Er
Er = Dr
Dr = Cr
Cr = ROL(Br, 10)
Br = T
```

**Key Points:**
- Left line uses rounds 0→79
- Right line uses rounds 79→0 (reversed)
- Different constants (K vs K')
- Different shift amounts (s vs s')
- Different word selection (r vs r')

#### 3.4 Update Hash Values

After 80 rounds, combine the results:

```
T   = h1 + C + Dr
h1  = h2 + D + Er
h2  = h3 + E + Ar
h3  = h4 + A + Br
h4  = h0 + B + Cr
h0  = T
```

### Step 4: Produce Final Output

Concatenate h0, h1, h2, h3, h4 in **little-endian** format:

```
Hash = little_endian(h0) || little_endian(h1) || little_endian(h2) ||
       little_endian(h3) || little_endian(h4)
```

Result: 160-bit hash value (40 hex characters)

---

## Mathematical Operations

### Boolean Functions f(j, x, y, z)

Five different functions are used across the 80 rounds:

#### Rounds 0-15 (f₁)

```
f(j, x, y, z) = x ⊕ y ⊕ z
```

**Operation:** XOR
**Use:** Simple mixing

#### Rounds 16-31 (f₂)

```
f(j, x, y, z) = (x ∧ y) ∨ (¬x ∧ z)
```

**Operation:** Conditional (if x then y else z)
**Use:** Selection function

#### Rounds 32-47 (f₃)

```
f(j, x, y, z) = (x ∨ ¬y) ⊕ z
```

**Operation:** OR-NOT-XOR combination
**Use:** Nonlinear mixing

#### Rounds 48-63 (f₄)

```
f(j, x, y, z) = (x ∧ z) ∨ (y ∧ ¬z)
```

**Operation:** Conditional (if z then x else y)
**Use:** Another selection function

#### Rounds 64-79 (f₅)

```
f(j, x, y, z) = x ⊕ (y ∨ ¬z)
```

**Operation:** XOR-OR-NOT combination
**Use:** Final mixing

### Rotate Left (ROL)

Circular left shift by n positions:

```
ROL(x, n) = (x << n) | (x >> (32 - n))
```

**Example:**
```
x = 0x12345678
ROL(x, 4) = 0x23456781
```

### Little-Endian Conversion

Convert 32-bit word to little-endian byte order:

```
Original:      0x12345678
Little-endian: 0x78563412

Bytes: [78] [56] [34] [12]
```

**Implementation:**
```python
def little_endian(value):
    # Convert 0x12345678 to "78563412"
    hex_str = format(value, '08x')
    return ''.join([hex_str[i:i+2] for i in range(6, -1, -2)])
```

---

## Constants and Tables

### Left Line Constants (K[i])

```
K[0] = 0x00000000  (rounds  0-15)
K[1] = 0x5A827999  (rounds 16-31)
K[2] = 0x6ED9EBA1  (rounds 32-47)
K[3] = 0x8F1BBCDC  (rounds 48-63)
K[4] = 0xA953FD4E  (rounds 64-79)
```

**Derivation:**
- K[1] = ⌊2³⁰ × √2⌋
- K[2] = ⌊2³⁰ × √3⌋
- K[3] = ⌊2³⁰ × √5⌋
- K[4] = ⌊2³⁰ × √7⌋

### Right Line Constants (K'[i])

```
K'[0] = 0x50A28BE6  (rounds  0-15)
K'[1] = 0x5C4DD124  (rounds 16-31)
K'[2] = 0x6D703EF3  (rounds 32-47)
K'[3] = 0x7A6D76E9  (rounds 48-63)
K'[4] = 0x00000000  (rounds 64-79)
```

**Derivation:**
- K'[0] = ⌊2³⁰ × ∛2⌋
- K'[1] = ⌊2³⁰ × ∛3⌋
- K'[2] = ⌊2³⁰ × ∛5⌋
- K'[3] = ⌊2³⁰ × ∛7⌋

### Shift Amounts (s[j] and s'[j])

#### Left Line Shifts (s[j])

```
Round   0-15: 11,14,15,12, 5, 8, 7, 9,11,13,14,15, 6, 7, 9, 8
Round  16-31:  7, 6, 8,13,11, 9, 7,15, 7,12,15, 9,11, 7,13,12
Round  32-47: 11,13, 6, 7,14, 9,13,15,14, 8,13, 6, 5,12, 7, 5
Round  48-63: 11,12,14,15,14,15, 9, 8, 9,14, 5, 6, 8, 6, 5,12
Round  64-79:  9,15, 5,11, 6, 8,13,12, 5,12,13,14,11, 8, 5, 6
```

#### Right Line Shifts (s'[j])

```
Round   0-15:  8, 9, 9,11,13,15,15, 5, 7, 7, 8,11,14,14,12, 6
Round  16-31:  9,13,15, 7,12, 8, 9,11, 7, 7,12, 7, 6,15,13,11
Round  32-47:  9, 7,15,11, 8, 6, 6,14,12,13, 5,14,13,13, 7, 5
Round  48-63: 15, 5, 8,11,14,14, 6,14, 6, 9,12, 9,12, 5,15, 8
Round  64-79:  8, 5,12, 9,12, 5,14, 6, 8,13, 6, 5,15,13,11,11
```

### Word Selection (r[j] and r'[j])

#### Left Line Word Selection (r[j])

```
Round   0-15:  0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15
Round  16-31:  7, 4,13, 1,10, 6,15, 3,12, 0, 9, 5, 2,14,11, 8
Round  32-47:  3,10,14, 4, 9,15, 8, 1, 2, 7, 0, 6,13,11, 5,12
Round  48-63:  1, 9,11,10, 0, 8,12, 4,13, 3, 7,15,14, 5, 6, 2
Round  64-79:  4, 0, 5, 9, 7,12, 2,10,14, 1, 3, 8,11, 6,15,13
```

#### Right Line Word Selection (r'[j])

```
Round   0-15:  5,14, 7, 0, 9, 2,11, 4,13, 6,15, 8, 1,10, 3,12
Round  16-31:  6,11, 3, 7, 0,13, 5,10,14,15, 8,12, 4, 9, 1, 2
Round  32-47: 15, 5, 1, 3, 7,14, 6, 9,11, 8,12, 2,10, 0, 4,13
Round  48-63:  8, 6, 4, 1, 3,11,15, 0, 5,12, 2,13, 9, 7,10,14
Round  64-79: 12,15,10, 4, 1, 5, 8, 7, 6, 2,13,14, 0, 3, 9,11
```

**Pattern:** Permutations designed to ensure all message words are used in non-sequential order, improving diffusion.

---

## Bitcoin Usage

### Hash160 Function

Bitcoin uses RIPEMD-160 as part of the **Hash160** function:

```
Hash160(data) = RIPEMD160(SHA256(data))
```

**Steps:**
1. Compute SHA-256 hash of input data
2. Compute RIPEMD-160 hash of the SHA-256 result
3. Result is 160-bit (20-byte) hash

### Bitcoin Address Generation

```
Public Key (ECDSA, 65 or 33 bytes)
    ↓
SHA-256 (256-bit hash)
    ↓
RIPEMD-160 (160-bit hash) ← Hash160
    ↓
Add version byte (0x00 for mainnet)
    ↓
SHA-256 (checksum step 1)
    ↓
SHA-256 (checksum step 2)
    ↓
Take first 4 bytes as checksum
    ↓
Append checksum to versioned hash
    ↓
Base58 encoding
    ↓
Bitcoin Address (starts with '1')
```

**Example:**

```
Public Key:  04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb6
             49f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f

SHA-256:     600FFE422B4E00731A59557A5CCA46CC183944191006324A447BDB2D98D4B408

RIPEMD-160:  010966776006953D5567439E5E39F86A0D273BEE

Version+Hash: 00010966776006953D5567439E5E39F86A0D273BEE

Checksum:    F9BEB4D9 (first 4 bytes of double SHA-256)

With Checksum: 00010966776006953D5567439E5E39F86A0D273BEEF9BEB4D9

Base58:      16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM
```

### Why RIPEMD-160 in Bitcoin?

1. **Shorter addresses:** 160 bits vs 256 bits (SHA-256 alone)
2. **Two hash functions:** Provides defense in depth
3. **Different designers:** SHA-256 (NSA) and RIPEMD-160 (academic), reduces risk
4. **Proven security:** Well-studied algorithm from 1996

---

## Implementation Details

### Pseudocode

```
function RIPEMD160(message):
    # Step 1: Padding
    padded = pad_message(message)

    # Step 2: Initialize
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    # Step 3: Process blocks
    for each 512-bit block in padded:
        X[0..15] = break_into_words(block)

        A, B, C, D, E = h0, h1, h2, h3, h4
        Ar, Br, Cr, Dr, Er = h0, h1, h2, h3, h4

        for j = 0 to 79:
            # Left line
            T = ROL(A + f(j, B, C, D) + X[r[j]] + K[j/16], s[j]) + E
            A, B, C, D, E = E, T, ROL(B, 10), C, D

            # Right line
            T = ROL(Ar + f(79-j, Br, Cr, Dr) + X[r'[j]] + K'[j/16], s'[j]) + Er
            Ar, Br, Cr, Dr, Er = Er, T, ROL(Br, 10), Cr, Dr

        # Update hash
        T = h1 + C + Dr
        h1 = h2 + D + Er
        h2 = h3 + E + Ar
        h3 = h4 + A + Br
        h4 = h0 + B + Cr
        h0 = T

    # Step 4: Output
    return little_endian(h0) || little_endian(h1) ||
           little_endian(h2) || little_endian(h3) || little_endian(h4)
```

### Python Implementation Notes

```python
# 32-bit arithmetic (use modulo)
mask = 0xFFFFFFFF  # 2^32
result = (a + b) & mask

# Or use % for modulo
result = (a + b) % (2**32)

# Rotate left
def ROL(value, n):
    return ((value << n) | (value >> (32 - n))) & 0xFFFFFFFF

# Little-endian conversion
def little_endian(word):
    # Convert 32-bit word to little-endian hex string
    return ''.join([format((word >> (8*i)) & 0xFF, '02x') for i in range(4)])
```

### Common Pitfalls

1. **Forgetting modulo 2³²:** All additions must wrap at 32 bits
2. **Endianness errors:** Bitcoin uses little-endian throughout
3. **Index errors:** r[j] and r'[j] select different words
4. **Function selection:** Use correct f(j) for each round
5. **Final combination:** Don't forget to combine left and right lines

---

## Test Vectors

### Official Test Vectors

#### Test 1: Empty String

```
Input:  "" (empty)
Output: 9c1185a5c5e9fc54612808977ee8f548b2258d31
```

#### Test 2: Single Character 'a'

```
Input:  "a"
Hex:    61
Output: 0bdc9d2d256b3ee9daae347be6f4dc835a467ffe
```

#### Test 3: String 'abc'

```
Input:  "abc"
Hex:    616263
Output: 8eb208f7e05d987a9b044a8e98c6b087f15a0bfc
```

#### Test 4: Message "message digest"

```
Input:  "message digest"
Hex:    6d65737361676520646967657374
Output: 5d0689ef49d2fae572b881b123a85ffa21595f36
```

#### Test 5: Lowercase Alphabet

```
Input:  "abcdefghijklmnopqrstuvwxyz"
Output: f71c27109c692c1b56bbdceb5b9d2865b3708dbc
```

#### Test 6: Alphanumeric

```
Input:  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
Output: b0e20b6e3116640286ed3a87a5713079b21f5189
```

#### Test 7: Repeated Digits

```
Input:  "12345678901234567890123456789012345678901234567890123456789012345678901234567890"
        (8 repetitions of "1234567890")
Output: 9b752e45573d4b39f4dbd3323cab82bf63326bfb
```

### Verification

Use these test vectors to verify your implementation:

```python
assert RIPEMD160('') == '9c1185a5c5e9fc54612808977ee8f548b2258d31'
assert RIPEMD160('61') == '0bdc9d2d256b3ee9daae347be6f4dc835a467ffe'
assert RIPEMD160('616263') == '8eb208f7e05d987a9b044a8e98c6b087f15a0bfc'
```

---

## Security Considerations

### Collision Resistance

**Definition:** Computationally infeasible to find two different inputs that produce the same hash.

**RIPEMD-160:**
- Theoretical collision resistance: 2⁸⁰ operations
- No practical collisions found as of 2024
- Considered secure for this property

### Preimage Resistance

**Definition:** Given hash H, computationally infeasible to find input M such that hash(M) = H.

**RIPEMD-160:**
- Theoretical preimage resistance: 2¹⁶⁰ operations
- No practical preimage attacks known
- Full 160-bit security

### Second Preimage Resistance

**Definition:** Given input M₁, computationally infeasible to find M₂ ≠ M₁ such that hash(M₁) = hash(M₂).

**RIPEMD-160:**
- Theoretical resistance: 2¹⁶⁰ operations
- No practical attacks known

### Known Weaknesses

1. **Reduced Round Attacks:**
   - Collisions found for 48 rounds (out of 80)
   - Not a practical threat to full 80-round version

2. **Smaller Output:**
   - 160 bits is smaller than SHA-256 (256 bits)
   - More vulnerable to birthday attacks
   - Still considered secure for most applications

3. **Age:**
   - Designed in 1996, less scrutiny than SHA-2/SHA-3
   - Not recommended for new systems (prefer SHA-256+)

### Bitcoin Security Context

**Why it's still secure in Bitcoin:**

1. **Defense in depth:** Used with SHA-256 (Hash160)
2. **Specific use case:** Only for address generation
3. **Not directly exposed:** Public key hash, not message hash
4. **Economic incentive:** Would need to break both SHA-256 and RIPEMD-160

---

## Comparison with Other Hashes

| Feature | RIPEMD-160 | SHA-1 | SHA-256 |
|---------|------------|-------|---------|
| Output Size | 160 bits | 160 bits | 256 bits |
| Block Size | 512 bits | 512 bits | 512 bits |
| Rounds | 80 (2×40) | 80 | 64 |
| Design | Dual line | Single line | Single line |
| Designer | Academic | NSA | NSA |
| Year | 1996 | 1995 | 2001 |
| Collisions | None found | Found (2017) | None found |
| Speed | Medium | Fast | Medium |
| Security | Good | Broken | Excellent |

**Recommendation:** For new applications, use SHA-256 or SHA-3. RIPEMD-160 is acceptable in Bitcoin's Hash160 context.

---

## References

### Official Specification

- **Original Paper:** "RIPEMD-160: A Strengthened Version of RIPEMD" by Hans Dobbertin, Antoon Bosselaers, and Bart Preneel (1996)
- **Homepage:** https://homes.esat.kuleuven.be/~bosselae/ripemd160.html

### Bitcoin Documentation

- **Bitcoin Wiki:** https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
- **Bitcoin Developer Guide:** https://bitcoin.org/en/developer-guide

### Implementations

- **OpenSSL:** Widely used C implementation
- **Python hashlib:** `hashlib.new('ripemd160')`
- **This Project:** `cryptography/ripemd160.py` (educational implementation)

### Related Reading

- **Applied Cryptography** by Bruce Schneier
- **Handbook of Applied Cryptography** by Menezes, van Oorschot, and Vanstone
- **FIPS 180-4:** Secure Hash Standard (compares with SHA family)

### Additional Resources

#### Academic Papers
- [RIPEMD-160 PDF Specification (AB-9601)](http://homes.esat.kuleuven.be/~bosselae/ripemd160/pdf/AB-9601/AB-9601.pdf)
- [COSIC Publications - Article 317](https://www.esat.kuleuven.be/cosic/publications/article-317.pdf)
- [Hash Functions Presentation](http://people.chu.edu.tw/~chlee/Crypto/Crypto9_1p.pdf)

#### Implementation Examples
- [Rosetta Code - RIPEMD-160 in FreeBASIC](https://rosettacode.org/wiki/RIPEMD-160#FreeBASIC)
- [PyCrypto RIPEMD-160 C Implementation](https://github.com/dlitz/pycrypto/blob/master/src/RIPEMD160.c)

#### Stack Exchange Discussions
- [How does RIPEMD-160 pad the message?](http://crypto.stackexchange.com/questions/32400/how-does-ripemd160-pad-the-message)
- [What is wrong with my RIPEMD-160 Python code?](http://stackoverflow.com/questions/2124165/what-is-wrong-with-my-ripemd160-python-code)

#### Presentations
- [Hash Functions Overview - SlideShare](http://www.slideshare.net/TazoAl1/hash-49022010)

---

## Appendix: Formula Quick Reference

### Core Formula

```
For round j (0 ≤ j < 80):

LEFT:  T = ROL(A + f(j, B, C, D) + X[r[j]] + K[j/16], s[j]) + E
       (A, B, C, D, E) ← (E, T, ROL(B, 10), C, D)

RIGHT: T = ROL(Ar + f(79-j, Br, Cr, Dr) + X[r'[j]] + K'[j/16], s'[j]) + Er
       (Ar, Br, Cr, Dr, Er) ← (Er, T, ROL(Br, 10), Cr, Dr)
```

### Final Combination

```
T  = h1 + C + Dr
h1 = h2 + D + Er
h2 = h3 + E + Ar
h3 = h4 + A + Br
h4 = h0 + B + Cr
h0 = T
```

### Padding Formula

```
Padded = Message || 1 || 0^k || length(Message)
where k = (448 - (length(Message) + 1)) mod 512
```

---

**Document Version:** 1.0
**Last Updated:** 2024
**Maintained By:** Bitcoin Code Educational Project
