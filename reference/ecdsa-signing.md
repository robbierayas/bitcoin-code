# ECDSA Digital Signatures

Complete guide to Elliptic Curve Digital Signature Algorithm (ECDSA) as used in Bitcoin.

## Overview

Bitcoin uses ECDSA with the secp256k1 elliptic curve for:
- **Transaction signing** - Prove ownership of coins
- **Transaction verification** - Validate signatures
- **Key pair generation** - Create public keys from private keys

## Secp256k1 Curve Parameters

### Elliptic Curve Equation
```
E: y² = x³ + 7
```

This is the Weierstrass form where:
- **a** = 0
- **b** = 7

### Base Point G (Generator Point)

**Compressed form:**
```
G = 02 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798
```

**Uncompressed form:**
```
G = 04 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798
       483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8
```

### Order and Cofactor

**Order n of G:**
```
n = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141
```

**Cofactor h:**
```
h = 01
```

## Key Creation

### Private Key
- **Symbol:** d_A
- **Type:** Integer
- **Range:** Randomly selected in the interval [1, n-1]
- **Size:** 256 bits (32 bytes)

### Public Key
- **Symbol:** Q_A
- **Formula:** Q_A = d_A × G
- **Note:** × denotes elliptic curve point multiplication by a scalar
- **Size:**
  - Uncompressed: 65 bytes (0x04 + x + y)
  - Compressed: 33 bytes (0x02/0x03 + x)

### Point Multiplication
Elliptic curve point multiplication is repeated point addition:
- d_A × G = G + G + ... + G (d_A times)
- Uses efficient algorithms like double-and-add

## Transaction Signing

### Message to Sign

In Bitcoin, the message to be signed is the transaction with specific modifications:

**Message (m):**
- `TXCopy.serialize()` - Serialized transaction
- Includes `scriptPubKey` from the previous output being spent
- See [OP_CHECKSIG](https://en.bitcoin.it/wiki/OP_CHECKSIG)

**Example scriptPubKey:**
```hex
76a914bcadb700c24da04b17feb9aa9bd71e368a4b623c88ac
```

This is a standard P2PKH (Pay-to-PubKey-Hash) script.

### Signature Generation Algorithm

**Inputs:**
- Private key: d_A
- Message: m
- Curve parameters: G, n

**Steps:**

#### Step 1: Hash the Message
```
e = SHA256(m)
```

#### Step 2: Truncate Hash
Let z be the L_n leftmost bits of e, where L_n is the bit length of the group order n.

For secp256k1:
- L_n = 256 bits
- So z = e (full hash)

#### Step 3: Generate Random k
Select a cryptographically secure random integer k from [1, n-1].

**Critical:** k must be truly random and never reused!
- Reusing k with different messages leaks the private key
- Use RFC 6979 deterministic k generation for safety

#### Step 4: Calculate Curve Point
```
(x₁, y₁) = k × G
```

Calculate the curve point by multiplying the generator G by k.

#### Step 5: Calculate r
```
r = x₁ mod n
```

If r = 0, go back to step 3 and generate a new k.

#### Step 6: Calculate s
```
s = k⁻¹ × (z + r × d_A) mod n
```

If s = 0, go back to step 3 and generate a new k.

Where:
- k⁻¹ is the multiplicative inverse of k modulo n
- All operations are modulo n

#### Step 7: Output Signature
The signature is the pair **(r, s)**.

**Encoding:**
- Bitcoin uses DER (Distinguished Encoding Rules) format
- Both r and s are encoded as integers
- Total signature size: typically 70-72 bytes

## Signature Verification

### Public Key Validation

Before verifying, Bob must validate Alice's public key Q_A:

#### Step 1: Check Not Identity
Verify Q_A ≠ O (point at infinity)

#### Step 2: Validate Coordinates
Check that Q_A coordinates are valid field elements:
- 0 ≤ x < p
- 0 ≤ y < p

#### Step 3: Check On Curve
Verify Q_A lies on the elliptic curve:
```
y² ≡ x³ + 7 (mod p)
```

#### Step 4: Check Order
Verify n × Q_A = O (point at infinity)

This ensures Q_A has the correct order.

### Verification Algorithm

**Inputs:**
- Public key: Q_A
- Message: m
- Signature: (r, s)
- Curve parameters: G, n

**Steps:**

#### Step 1: Validate Signature Values
Verify that r and s are integers in [1, n-1].
If not, the signature is invalid.

#### Step 2: Hash the Message
```
e = SHA256(m)
```

For Bitcoin transactions:
```
e = SHA256(SHA256(m))
```
(Double SHA-256)

#### Step 3: Truncate Hash
Let z be the L_n leftmost bits of e.

#### Step 4: Calculate w
```
w = s⁻¹ mod n
```

Where s⁻¹ is the multiplicative inverse of s modulo n.

#### Step 5: Calculate u₁ and u₂
```
u₁ = z × w mod n
u₂ = r × w mod n
```

#### Step 6: Calculate Curve Point
```
(x₁, y₁) = u₁ × G + u₂ × Q_A
```

This is a linear combination of two elliptic curve points.

#### Step 7: Verify Signature
The signature is **valid** if:
```
r ≡ x₁ (mod n)
```

Otherwise, the signature is **invalid**.

## Bitcoin-Specific Implementation

### Function Call
```python
ECDSA_CheckSignature(pubkeyStr, SigStr, sha256(sha256(m)))
```

### Double Hashing
Bitcoin uses double SHA-256 for extra security:
```
hash = SHA256(SHA256(message))
```

### DER Encoding
Signatures in Bitcoin transactions use DER encoding:
```
0x30 [total-length] 0x02 [R-length] [R] 0x02 [S-length] [S] [sighash-type]
```

**Sighash types:**
- `0x01` - SIGHASH_ALL (most common)
- `0x02` - SIGHASH_NONE
- `0x03` - SIGHASH_SINGLE
- `0x81` - SIGHASH_ALL | SIGHASH_ANYONECANPAY

## Security Considerations

### Critical Rules

1. **Never Reuse k**
   - Reusing k with two different messages reveals the private key
   - Use deterministic k generation (RFC 6979)

2. **Use Cryptographically Secure RNG**
   - k must be unpredictable
   - Bad randomness = compromised private key

3. **Validate All Inputs**
   - Check signature values are in valid range
   - Validate public key is on curve
   - Verify curve point calculations don't result in O

4. **Constant-Time Operations**
   - Use constant-time implementations to prevent timing attacks
   - Especially important for scalar multiplication

### Known Attacks

**k Reuse Attack:**
If k is reused for two signatures (r₁, s₁) and (r₂, s₂):
```
d_A = (s₁ × z₂ - s₂ × z₁) / (s₂ × r - s₁ × r) mod n
```

**Biased k Attack:**
If even a few bits of k are known or predictable, lattice attacks can recover d_A.

**Side-Channel Attacks:**
- Timing analysis
- Power analysis
- Electromagnetic emissions
- Fault injection

## Example Verification

### Test Online
[ECDSA Sample Tool](https://kjur.github.io/jsrsasign/sample-ecdsa.html)

Use this tool to:
- Generate key pairs
- Sign messages
- Verify signatures
- Test with custom parameters

## Mathematical Background

### Why It Works

The verification works because:
```
u₁ × G + u₂ × Q_A
= u₁ × G + u₂ × (d_A × G)
= (u₁ + u₂ × d_A) × G
= (z × w + r × w × d_A) × G
= w × (z + r × d_A) × G
= (z + r × d_A) / s × G
= k × G          (from signature generation)
= (x₁, y₁)
```

Therefore x₁ mod n = r, proving the signature is valid.

### Elliptic Curve Scalar Multiplication

**Double-and-Add Algorithm:**
```
Result = O (identity)
For each bit in scalar k (from MSB to LSB):
    Result = 2 × Result (point doubling)
    If bit is 1:
        Result = Result + G (point addition)
Return Result
```

More efficient algorithms exist (windowing, NAF, etc.)

## References

### Standards and Specifications
- [ECDSA Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [secp256k1 Specification](https://en.bitcoin.it/wiki/Secp256k1)
- [RFC 6979](https://tools.ietf.org/html/rfc6979) - Deterministic ECDSA

### Bitcoin-Specific
- [OP_CHECKSIG](https://en.bitcoin.it/wiki/OP_CHECKSIG)
- [Transaction Signature](http://bitcoin.stackexchange.com/questions/37093/what-goes-in-to-the-message-of-a-transaction-signature)

### Scalar Multiplication
- [ECC Point Multiplication](http://crypto.stackexchange.com/questions/3907/how-does-one-calculate-the-scalar-multiplication-on-elliptic-curves)

### Implementation Examples
- [Ken Shirriff's Bitcoin Code](http://www.righto.com/search?q=bitcoin)
- [Bitcoin Code Repository](https://github.com/shirriff/bitcoin-code)

## Common Pitfalls

1. **Not validating the public key** - Always check Q_A is on the curve
2. **Using weak RNG for k** - Use hardware RNG or deterministic RFC 6979
3. **Reusing k values** - Fatal security flaw
4. **Integer overflow** - All operations must be mod n
5. **Not checking for O** - Point at infinity should be rejected
6. **Timing attacks** - Use constant-time implementations
7. **DER encoding errors** - Malformed signatures can bypass checks

## Testing

Verify your implementation with:
- Official test vectors
- Known transaction signatures from blockchain
- Cross-reference with established libraries
- Test edge cases (r=1, s=1, max values, etc.)
