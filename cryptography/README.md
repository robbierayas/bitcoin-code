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

### keyUtils.py ✓
**ECDSA key management and Bitcoin address generation**

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

**Uses:** ECDSA secp256k1, SHA-256, RIPEMD-160, base58Utils.base58CheckEncode

**Dependencies:** base58Utils (for WIF and address encoding)

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

**Total:** 35 tests pass ✓ (11 base58 + 9 keyUtils + 15 RIPEMD-160)

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
| keyUtils.py | ~50 | ✓ Working | 9/9 | **Production** |
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

## Algorithm Documentation

For comprehensive RIPEMD-160 algorithm documentation, see:
- **../reference/ripemd160.md** - Complete algorithm specification with test vectors

## References

- [Official RIPEMD-160 spec](https://homes.esat.kuleuven.be/~bosselae/ripemd160.html)
- [Bitcoin Wiki - Technical background](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses)
- [RIPEMD-160 test vectors](https://homes.esat.kuleuven.be/~bosselae/ripemd160/pdf/AB-9601/AB-9601.pdf)
