# Cryptography Module

Custom cryptographic implementations for educational purposes.

## Overview

This module implements the cryptographic primitives used in Bitcoin:
- **ECDSA** - secp256k1 elliptic curve key generation and signing
- **RIPEMD-160** - Hash function for Bitcoin addresses
- **Key Management** - WIF format, address generation
- **Signatures** - DER encoding, signature verification

**WARNING:** Educational only. Not security audited. Use standard libraries for production.

## Files

### base58Utils.py ✓
**Base58 and Base256 encoding utilities**

- Base58 encoding/decoding
- Base256 encoding/decoding
- Base58Check encoding with checksums
- Leading character counting

**Tests:** cryptography/tests/test_base58Utils.py (11 tests)

**Main functions:**
```python
from cryptography import base58Utils

# Base58 encoding
encoded = base58Utils.base58encode(12345)
decoded = base58Utils.base58decode(encoded)

# Base256 encoding
byte_data = base58Utils.base256encode(0x4142)
number = base58Utils.base256decode(b'AB')

# Base58Check (Bitcoin addresses, WIF)
address = base58Utils.base58CheckEncode(0x00, hash160_bytes)
payload = base58Utils.base58CheckDecode(address)
```

**Used by:** keyUtils for WIF and address encoding

### keypair.py ✓ (NEW - OBJECT ORIENTED)
**Bitcoin ECDSA KeyPair class**

Object-oriented key management with public/private key encapsulation.

**Class: KeyPair**
- `publickey` - Public attribute (hex string)
- `_privatekey` - Private attribute (hex string)
- Constructor takes private key hex

**Tests:** cryptography/tests/test_keypair.py (24 tests)

**Main usage:**
```python
from cryptography.keypair import KeyPair

# Create from private key
keypair = KeyPair(private_key_hex)

# Access public key (public attribute)
pub = keypair.publickey

# Get private key (read-only method)
priv = keypair.get_private_key()

# Generate address
address = keypair.get_address()

# WIF conversion
wif = keypair.to_wif()
keypair = KeyPair.from_wif(wif)

# Generate random keypair
keypair = KeyPair.generate()

# Sign and verify
signature = keypair.sign(message_hash)
is_valid = keypair.verify(message_hash, signature)
```

**Uses:** ECDSA secp256k1, SHA-256, RIPEMD-160, base58Utils

**Dependencies:** base58Utils

### keyUtils.py ✓
**ECDSA key management functions (legacy API)**

Function-based API maintained for backward compatibility.
**Now uses KeyPair class internally.**

- Private key ↔ WIF (Wallet Import Format) conversion
- ECDSA key pair generation (secp256k1)
- Public key from private key
- Bitcoin address from public/private key
- DER signature encoding
- ScriptPubKey generation

**Tests:** cryptography/tests/test_keyUtils.py (9 tests)

**Main functions:**
```python
from cryptography import keyUtils

# WIF conversion
wif = keyUtils.privateKeyToWif(private_key_hex)
key = keyUtils.wifToPrivateKey(wif)

# Key generation
public_key = keyUtils.privateKeyToPublicKey(private_key_hex)
address = keyUtils.keyToAddr(private_key_hex)
address = keyUtils.pubKeyToAddr(public_key_hex)

# Signatures
hex_sig = keyUtils.derSigToHexSig(der_signature)
script = keyUtils.addrHashToScriptPubKey(address)
```

**Note:** For new code, prefer using KeyPair class for better OOP design.

**Uses:** KeyPair class, ECDSA secp256k1, SHA-256, RIPEMD-160

**Dependencies:** keypair, base58Utils

### ripemd160.py ✓ (USE THIS ONE)
**Clean, well-documented RIPEMD-160 implementation**

- Professional implementation (~280 lines with extensive comments)
- Fully documented with docstrings
- Clear section markers for different parts of algorithm
- Includes verification test
- **Python 3 compatible**
- **All tests pass (15/15)**

**Main function:**
```python
from ripemd160 import RIPEMD160
hash = RIPEMD160('616263')  # Hash of 'abc' in hex
# Returns: '8eb208f7e05d987a9b044a8e98c6b087f15a0bfc'
```

**Status:** ✓ Verified working - use for production

### ripemd160_educational.py
**Verbose RIPEMD-160 with extensive debugging output**

- Educational version with lots of print statements
- Shows step-by-step execution
- Good for learning how RIPEMD-160 works internally
- Takes SHA-256 hash first, then applies RIPEMD-160
- May have compatibility issues

**Status:** Educational/reference - not recommended for use

### ripemd160_backup.py
**Backup copy of educational version**

- Preserved as historical reference
- Similar to ripemd160_educational.py
- Kept for comparison purposes

**Status:** Archive only - do not use

### rollback.py
**Experimental RIPEMD-160 reverse engineering**

- Attempts to reverse Bitcoin addresses
- Brute force approach to find intermediate hash values
- Cryptographic research project
- **No tests yet** - highly experimental

**Status:** Research only - experimental

## Testing

Comprehensive test suites available.

**Run tests:**
```bash
cd cryptography/tests
python test_base58Utils.py   # 11 tests - Base58/Base256 encoding
python test_keyUtils.py      # 9 tests - ECDSA, WIF, addresses
python test_ripemd160.py     # 15 tests - RIPEMD-160 algorithm
```

**base58Utils test coverage:**
- Base58 encoding/decoding roundtrips
- Base256 encoding/decoding
- Base58Check encoding/decoding
- Leading character counting
- WIF encoding verification

**keyUtils test coverage:**
- Private key ↔ WIF conversion
- Key to address generation
- Multiple wallet formats (blockchain.info, multibit, bitaddress.org)
- DER signature encoding/decoding
- Transaction signature verification

**RIPEMD-160 test coverage:**
- Empty string hash
- Single character 'a'
- String 'abc'
- 'message digest'
- Lowercase alphabet a-z
- Mixed case alphanumeric
- Repeated digits
- Bitcoin public key example
- Output format validation
- Deterministic behavior
- Utility functions (makehex, makebin, ROL, little_end)

**Total:** 59 tests pass ✓ (11 base58 + 24 keypair + 9 keyUtils + 15 RIPEMD-160)

## Usage

### Production Use
```python
from ripemd160 import RIPEMD160

# Hash hex data
result = RIPEMD160('616263')  # 'abc'
print(result)
# Output: 8eb208f7e05d987a9b044a8e98c6b087f15a0bfc
```

### Bitcoin Address Generation
```python
import hashlib
from ripemd160 import RIPEMD160

# Public key (example)
pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'

# SHA-256 then RIPEMD-160
sha256_hash = hashlib.sha256(bytes.fromhex(pubkey)).hexdigest()
ripemd_hash = RIPEMD160(sha256_hash)

print("Hash160:", ripemd_hash)
```

### Educational/Learning
```python
# Use ripemd160_educational.py to see step-by-step output
# (not recommended for actual use)
```

## File Comparison

| File | Lines | Status | Tests | Use Case |
|------|-------|--------|-------|----------|
| base58Utils.py | ~100 | ✓ Working | 11/11 | **Production** |
| keypair.py | ~200 | ✓ Working | 24/24 | **Production (OOP)** |
| keyUtils.py | ~120 | ✓ Working | 9/9 | **Production (Legacy)** |
| ripemd160.py | ~280 | ✓ Working | 15/15 | **Production** |
| ripemd160_educational.py | ~301 | Educational | N/A | Learning |
| ripemd160_backup.py | ~301 | Archive | N/A | Reference |
| rollback.py | ~451 | Experimental | 0 | Research |

## RIPEMD-160 Algorithm

### Overview
- **Output:** 160-bit (20-byte) hash
- **Block size:** 512 bits
- **Rounds:** 80 (2 parallel lines of 40 rounds each)
- **Used in Bitcoin** for address generation

### Algorithm Structure
1. **Preprocessing:** Pad message and append length
2. **Initialize:** Set initial hash values (5 × 32-bit words)
3. **Process blocks:** 512-bit blocks with dual parallel computation
4. **Finalize:** Combine left and right line results

### Bitcoin Usage
```
Public Key (ECDSA, 65 bytes uncompressed)
  ↓ SHA-256
256-bit hash
  ↓ RIPEMD-160
160-bit hash (Hash160)
  ↓ Base58Check
Bitcoin Address
```

## Key Improvements in ripemd160.py

1. **Clear documentation** - Every function has docstrings
2. **Section markers** - Easy to find different parts of algorithm
3. **Comments** - Explains what each constant/array represents
4. **Python 3 compatible** - Uses `//` for integer division, `list(range())`
5. **Readable structure** - Separated utility functions from main algorithm
6. **Verification test** - Runs when executed directly

## Notes

- **base58Utils.py** - General-purpose Base58/Base256 encoding (no Bitcoin dependencies)
- **keyUtils.py** - ECDSA key management with Bitcoin-specific formats (WIF, addresses)
- **ripemd160.py** - Pure RIPEMD-160 implementation (production)
- **No dependencies on bitcoin/** - Cryptography module is self-contained
- **All implementations take hex input** - Not raw bytes (except base58Utils which handles both)
- **Output is hex string** - 40 characters (160 bits) for RIPEMD-160
- **Deterministic** - Same input always produces same output

## Security Warning

These are **educational implementations** for understanding Bitcoin internals.

**For production:**
- Use `hashlib.new('ripemd160')` (Python standard library)
- Or `Crypto.Hash.RIPEMD` (PyCrypto)
- These custom implementations are **not security audited**

## Detailed Algorithm Explanations

### Elliptic Curve Cryptography (ECDSA secp256k1)

#### The secp256k1 Curve

Bitcoin uses the secp256k1 elliptic curve:

**Curve equation:** `y² = x³ + 7 (mod p)`

**Parameters:**
- **p** = 2²⁵⁶ - 2³² - 977 (field prime, defines the finite field)
- **G** = Generator point (fixed starting point for all key generation)
  - Gx = `0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798`
  - Gy = `0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8`
- **n** = Order (number of valid private keys ≈ 1.158 × 10⁷⁷)
  - n = `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141`

**Order meaning:**
```
1 × G = G
2 × G = some point
3 × G = another point
...
n × G = point at infinity (wraps back to zero)
(n+1) × G = G (cycle repeats)
```

Valid private keys range from 1 to (n-1).

#### Private Key → Public Key (Point Multiplication)

**The one-way function:**
```
Public Key = k × G
```
Where k is the private key (secret number).

**Security:**
- **Easy direction:** k → Public Key (fast computation using double-and-add)
- **Hard direction:** Public Key → k (Elliptic Curve Discrete Logarithm Problem - computationally infeasible)

This one-way property is what makes Bitcoin secure!

#### Point Multiplication Algorithm (Double-and-Add)

Instead of adding G to itself k times, we use a binary approach:

**Example: Calculate 23 × G**

1. Convert to binary: 23 = 10111₂
2. Process left to right:
   - Bit 1: Result = G
   - Bit 0: Double → Result = 2G
   - Bit 1: Double → 4G, add G → Result = 5G
   - Bit 1: Double → 10G, add G → Result = 11G
   - Bit 1: Double → 22G, add G → Result = 23G

**Alternative (powers of 2):**
```
23 = 16 + 4 + 2 + 1
23G = (2⁴)G + (2²)G + (2¹)G + (2⁰)G

Calculate by repeated doubling:
G → 2G → 4G → 8G → 16G
Then add: 16G + 4G + 2G + G = 23G
```

This reduces a 256-bit multiplication to only ~256 doublings and ~128 additions (on average).

#### Point Addition Formulas

**Adding two different points P + Q = R:**

Given P(x₁, y₁) and Q(x₂, y₂):

```
Step 1: Calculate slope
s = (y₂ - y₁) × (x₂ - x₁)⁻¹ mod p

Step 2: Calculate x-coordinate of result
x₃ = (s × s) - x₁ - x₂ mod p

Step 3: Calculate y-coordinate of result
y₃ = s × (x₁ - x₃) - y₁ mod p

Result: R = (x₃, y₃)
```

**Point Doubling P + P = R:**

Given P(x₁, y₁):

```
Step 1: Calculate slope (tangent to curve)
s = (3 × x₁ × x₁) × (2 × y₁)⁻¹ mod p
(For secp256k1, a=0, so numerator is 3x₁²)

Step 2: Calculate x₃
x₃ = (s × s) - 2 × x₁ mod p

Step 3: Calculate y₃
y₃ = s × (x₁ - x₃) - y₁ mod p

Result: R = (x₃, y₃)
```

#### Modular Arithmetic

**Modular Inverse:**

Division doesn't exist in modular arithmetic. Instead of `a / b mod p`, we calculate:
```
a × b⁻¹ mod p
```

Where `b⁻¹` is the modular inverse: `b × b⁻¹ ≡ 1 (mod p)`

**Example:**
```
Find 5 / 3 mod 7

Step 1: Find 3⁻¹ mod 7
3 × ? ≡ 1 (mod 7)
3 × 5 = 15 = 2×7 + 1 ≡ 1 (mod 7)
So 3⁻¹ = 5

Step 2: Calculate
5 / 3 = 5 × 5 = 25 = 3×7 + 4 ≡ 4 (mod 7)
```

#### Public Key Formats

**Uncompressed (65 bytes):**
```
0x04 + x-coordinate (32 bytes) + y-coordinate (32 bytes)
```

**Compressed (33 bytes):**

Since `y² = x³ + 7`, if you know x, you can calculate y² and take the square root. However, there are TWO possible y values (y and -y mod p).

```
If y is even: 0x02 + x-coordinate (32 bytes)
If y is odd:  0x03 + x-coordinate (32 bytes)
```

The prefix byte tells which y value to use when reconstructing the full public key.

#### ECDSA Signature Creation

**Purpose:** Prove ownership of private key WITHOUT revealing it

**Signing process:**
```
1. Pick random number r (nonce)
2. Calculate R = r × G (point multiplication)
3. Get x-coordinate of R, call it r_x
4. Calculate: s = (z + r_x × k) / r mod n
   Where:
   - z = hash of transaction data
   - k = private key
   - n = curve order

Signature = (r_x, s)
```

**Verification (anyone can do this):**
```
1. Calculate: P = (z/s) × G + (r_x/s) × PublicKey
2. If P's x-coordinate equals r_x, signature is VALID
```

**Mathematical proof why this works:**
```
Since PublicKey = k × G:
P = (z/s) × G + (r_x/s) × (k × G)
P = (z/s + r_x × k/s) × G
P = ((z + r_x × k)/s) × G

Since s = (z + r_x × k)/r:
P = ((z + r_x × k) × r/(z + r_x × k)) × G
P = r × G = R ✓

The x-coordinates match!
```

### Public Key Visibility and Security

**Before spending (receiving only):**
- Address visible: `1ABC...` (Base58Check encoded)
- Public key: **HIDDEN** (only hash is in address)
- Private key: **SECRET**

**When spending (creating transaction):**
- Transaction input includes: `<signature> <public key>`
- Public key is now **VISIBLE** to everyone
- Network verifies:
  1. Hash(public key) matches the address you're spending from
  2. Signature is valid using the revealed public key

**Security implications:**
- Once you spend, your public key is exposed
- Quantum computers could potentially derive private key from public key
- Best practice: **Don't reuse addresses** after spending
- Use a new address for change outputs

### Hash Function Flow

**Complete Bitcoin address generation:**
```
Private Key (256-bit random number)
    ↓
ECDSA secp256k1 point multiplication (k × G)
    ↓
Public Key (x, y coordinates on curve)
    ↓
Compressed: 02/03 + x coordinate (33 bytes)
Uncompressed: 04 + x + y (65 bytes)
    ↓
SHA-256 hash (32 bytes)
    ↓
RIPEMD-160 hash (20 bytes) ← "Hash160"
    ↓
Add version byte (0x00 for mainnet P2PKH)
    ↓
SHA-256 twice for checksum
    ↓
Append first 4 bytes of checksum
    ↓
Base58 encode (preserving leading zeros as '1')
    ↓
Bitcoin Address (starts with '1' for P2PKH)
```

## Algorithm Documentation

For comprehensive RIPEMD-160 algorithm documentation, see:
- **../reference/ripemd160.md** - Complete algorithm specification with test vectors

## References

- [Official RIPEMD-160 spec](https://homes.esat.kuleuven.be/~bosselae/ripemd160.html)
- [Bitcoin Wiki - Technical background](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses)
- [RIPEMD-160 test vectors](https://homes.esat.kuleuven.be/~bosselae/ripemd160/pdf/AB-9601/AB-9601.pdf)
- [SEC 2: Recommended Elliptic Curve Domain Parameters](https://www.secg.org/sec2-v2.pdf) - secp256k1 specification
