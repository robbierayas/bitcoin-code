# Reference Documentation

Comprehensive algorithm and protocol documentation for Bitcoin education.

## Files Overview

| File | Size | Description |
|------|------|-------------|
| ripemd160.md | 750+ lines | Complete RIPEMD-160 algorithm specification |
| address-creation.md | 350+ lines | Bitcoin address generation guide |
| ecdsa-signing.md | 500+ lines | ECDSA signature algorithm for Bitcoin |
| test-vectors.md | 350+ lines | Test cases and verification examples |

## Detailed Contents

### ripemd160.md
**Complete RIPEMD-160 Algorithm Specification**

Comprehensive documentation covering:

#### Algorithm Details
- 160-bit cryptographic hash function
- Dual parallel computation lines (left and right)
- 80 rounds total (5 rounds × 16 steps per line)
- 512-bit block processing

#### Complete Specification
- Step-by-step algorithm breakdown
- Preprocessing (padding and length encoding)
- Hash computation with dual lines
- Finalization and combination

#### Constants and Tables
- Initial hash values (h0-h4)
- Left line constants (K0-K4)
- Right line constants (K'0-K'4)
- Shift amounts (s array - 80 values)
- Right shift amounts (s' array - 80 values)
- Message word selection (r and r' arrays)

#### Mathematical Operations
- 5 Boolean functions (f0-f4)
- Cyclic left rotation (ROL)
- Little-endian conversion
- Addition modulo 2³²

#### Bitcoin Usage
- Hash160 specification (SHA-256 + RIPEMD-160)
- Public key to address conversion
- Complete example with test vectors

#### Test Vectors
Official RIPEMD-160 test vectors:
- Empty string
- "a"
- "abc"
- "message digest"
- "abcdefghijklmnopqrstuvwxyz"
- Full alphanumeric string
- Repeated digits (8 × "1234567890")

#### References
- Official specification links
- Academic papers
- Implementation examples
- Stack Exchange discussions

### address-creation.md
**Bitcoin Address Generation Guide**

Complete step-by-step process:

#### Key Specifications
- Private key format (32 bytes)
- Public key formats (compressed/uncompressed)
- Public key hash (20 bytes)
- Address encoding (Base58Check)

#### 9-Step Process
1. Generate ECDSA key pair (secp256k1)
2. SHA-256 hash of public key
3. RIPEMD-160 hash
4. Add version byte (0x00 for mainnet)
5. First SHA-256 for checksum
6. Second SHA-256 for checksum
7. Extract 4-byte checksum
8. Create 25-byte binary address
9. Base58 encode to final address

#### Complete Examples
- Test Case 1: Full address generation with all intermediate values
- Test Case 2: From transaction public key hash
- Verification methods
- Online tools

#### Visual Flow
- Complete diagram from private key to address
- Formula quick reference
- Security considerations

### ecdsa-signing.md
**ECDSA Digital Signatures for Bitcoin**

Comprehensive signature documentation:

#### Secp256k1 Curve
- Elliptic curve equation: y² = x³ + 7
- Base point G (compressed and uncompressed)
- Order n and cofactor h
- Curve parameters

#### Key Creation
- Private key generation (256-bit random)
- Public key derivation (scalar multiplication)
- Point multiplication algorithms

#### Signature Generation
- Message preparation (transaction serialization)
- SHA-256 hashing
- Random k generation (RFC 6979)
- Calculate r and s values
- DER encoding

#### Signature Verification
- Public key validation (on-curve check)
- Signature value validation
- Hash computation
- Verification equation: r ≡ x₁ (mod n)

#### Security Considerations
- Never reuse k (critical!)
- Use cryptographically secure RNG
- Validate all inputs
- Constant-time operations
- Known attacks and mitigations

#### Bitcoin-Specific
- Double SHA-256 hashing
- DER signature encoding
- Sighash types (ALL, NONE, SINGLE)
- OP_CHECKSIG operation

#### Mathematical Background
- Why verification works (proof)
- Scalar multiplication algorithms
- Point addition/doubling formulas

### test-vectors.md
**Bitcoin Test Vectors and Examples**

Detailed test cases for verification:

#### Test Case 1: Complete Address Generation
- Private key: `a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f`
- All intermediate values shown
- SHA-256, RIPEMD-160 outputs
- Checksum calculation
- Final address: `1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy`

#### Test Case 2: From Transaction
- Public key hash: `bcadb700c24da04b17feb9aa9bd71e368a4b623c`
- Complete generation process
- Final address: `1JCe8z4jJVNXSjohjM4i9Hh813dLCNx2Sy`
- Associated scriptPubKey

#### Real Transaction Example
- Transaction ID on blockchain
- Link to blockchain explorer
- Verification methods

#### Verification Checklists
- Address generation checklist
- Signature verification checklist
- Common test errors and solutions

#### Online Tools
- Hash calculators
- Bitcoin tools (HASH160)
- Base58 converters
- ECDSA testers

#### Python Verification Example
Complete code to verify test cases step-by-step

## Usage

### For Learning
1. Start with **address-creation.md** to understand address generation
2. Study **ripemd160.md** for the hashing algorithm details
3. Read **ecdsa-signing.md** for transaction signing
4. Verify understanding with **test-vectors.md**

### For Implementation
1. Use **ripemd160.md** as algorithm reference
2. Follow **test-vectors.md** for test-driven development
3. Reference **address-creation.md** and **ecdsa-signing.md** for Bitcoin-specific details

### For Verification
All test vectors can be verified with:
- `../cryptography/ripemd160.py` - Production implementation
- `../cryptography/ripemd160_educational.py` - Educational implementation
- `../bitcoin/keyUtils.py` - Key and address utilities
- `../bitcoin/txnUtils.py` - Transaction utilities

## Referenced By

### Cryptography Module
- `cryptography/ripemd160.py` - Production implementation
- `cryptography/ripemd160_educational.py` - Educational implementation
- `cryptography/tests/` - Test suites

### Bitcoin Module
- `bitcoin/keyUtils.py` - Key utilities
- `bitcoin/txnUtils.py` - Transaction utilities
- `bitcoin/msgUtils.py` - P2P messages
- `bitcoin/tests/` - Bitcoin tests

## Quick Reference Links

### Bitcoin Standards
- [BIP 32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) - Hierarchical Deterministic Wallets
- [BIP 39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) - Mnemonic Seeds
- [BIP 44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) - Multi-Account Hierarchy

### Bitcoin Wiki
- [Technical Background](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses)
- [secp256k1](https://en.bitcoin.it/wiki/Secp256k1)
- [OP_CHECKSIG](https://en.bitcoin.it/wiki/OP_CHECKSIG)

### Cryptography Resources
- [RIPEMD-160 Official](https://homes.esat.kuleuven.be/~bosselae/ripemd160.html)
- [ECDSA Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [RFC 6979](https://tools.ietf.org/html/rfc6979) - Deterministic ECDSA

## Purpose

Educational reference for understanding:
- Bitcoin address generation process
- RIPEMD-160 cryptographic hash function
- ECDSA signature creation and verification
- Transaction signing mechanics
- How Bitcoin security works
- Why specific algorithms were chosen

## Notes

- All documentation is for **educational purposes only**
- Do **NOT** use these implementations for real Bitcoin transactions
- For production use:
  - Bitcoin Core
  - Established libraries (python-bitcoinlib, etc.)
  - Hardware wallets
  - Security-audited software

## Contributing

When adding reference documentation:
1. Include complete examples with all intermediate values
2. Provide test vectors for verification
3. Link to official specifications
4. Explain the "why" not just the "how"
5. Add security considerations
6. Include common pitfalls and solutions

## Version Information

**Last Updated:** 2024
**Maintained By:** Bitcoin Code Educational Project
**Based On:**
- Official Bitcoin protocol
- RIPEMD-160 specification (AB-9601)
- secp256k1 ECDSA standard
- Bitcoin Wiki documentation
