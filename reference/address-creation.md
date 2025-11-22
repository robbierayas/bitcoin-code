# Bitcoin Address Creation

Complete guide to creating Bitcoin addresses from private keys.

## Overview

Bitcoin addresses are generated through a multi-step process involving:
1. **ECDSA** elliptic curve cryptography (secp256k1)
2. **SHA-256** cryptographic hashing
3. **RIPEMD-160** hash function
4. **Base58Check** encoding

## Key Specifications

### Private Key
- **Size:** Always 32 bytes (256 bits)
- **Format:** Standard format is a 256-bit number
- **Range:** Between `0x01` and `0xFFFF FFFF FFFF FFFF FFFF FFFF FFFF FFFE BAAE DCE6 AF48 A03B BFD2 5E8C D036 4140`
- **Total values:** Nearly the entire range of 2^256 - 1 values
- **Standard:** Governed by secp256k1 ECDSA encryption standard

### Public Key
- **Uncompressed:** Always 65 bytes
  - 1 byte prefix (`0x04`)
  - 32 bytes X coordinate
  - 32 bytes Y coordinate
- **Compressed:** Always 33 bytes
  - 1 byte prefix (`0x02` or `0x03`)
  - 32 bytes X coordinate

### Public Key Hash
- **Size:** Always 20 bytes (160 bits)
- **Formula:** `PKHash = HASH160(PK) = RIPEMD160(SHA256(PK))`

## Address Creation Process

### Step-by-Step Guide

#### Step 1: Generate Key Pair
Choose a supported EC curve name and generate a key pair using secp256k1.

**Example:**
```
Private Key: a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f
Public Key:  0427d64b2de9f51ac1bf6b287088de3afcf67e8dd820848128cc27f71c18c5f8ba
             efe71cc14052b4989e33a17f4795022f70313561cb3ef3d0b599c49933daa6fd
```

#### Step 2: SHA-256 Hash of Public Key
Perform SHA-256 hashing on the public key (65 bytes).

**Result:** 32 bytes
```
SHA256(Public): f6c4d6736f912ffebe65fb1497aac2a111d037883f39b5d72ea0d39f216ed368
```

#### Step 3: RIPEMD-160 Hash
Perform RIPEMD-160 hashing on the result of SHA-256.

**Result:** 20 bytes
```
RIPEMD160(SHA256(PK)): f3cd5ddd30ad4d28f13cf195786f2e95e8914b22
```

**Verification:** Using HASH160 function gives address from PK.
Check with Base58Decode(HASH160).toLowerCase = `00||RIPEMD160(SHA256(PK))` - last4

#### Step 4: Add Version Byte
Add version byte in front of RIPEMD-160 hash.
- **Mainnet:** `0x00`
- **Testnet:** `0x6F`

**Result:**
```
00f3cd5ddd30ad4d28f13cf195786f2e95e8914b22
```

*Note: Steps 5-8 implement Base58Check encoding*

#### Step 5: First SHA-256 on Extended Hash
Perform SHA-256 hash on the extended RIPEMD-160 result.

**Result:**
```
9c618e84ba7bb0b6d208f7f57d9b92bdfb929efba53a3668469115a96105db90
```

#### Step 6: Second SHA-256
Perform SHA-256 hash on the result of the previous SHA-256 hash.

**Result:**
```
5c8492ba9c962bd90185764df1d68e106828d9608ebd42a81280e3d7ba7f41f7
```

#### Step 7: Extract Checksum
Take the first 4 bytes of the second SHA-256 hash. This is the address checksum.

**Checksum:**
```
5c8492ba
```

#### Step 8: Create Binary Address
Add the 4 checksum bytes at the end of extended RIPEMD-160 hash from step 4.

**Result:** 25-byte binary Bitcoin Address
```
00f3cd5ddd30ad4d28f13cf195786f2e95e8914b225c8492ba
```

#### Step 9: Base58 Encoding
Convert the result from a byte string into a base58 string using Base58Check encoding.

**Final Address:**
```
1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
```

This is the most commonly used Bitcoin Address format.

## Complete Formula

```
4checksumBytes = first4(SHA256(SHA256(00|PKHash)))
Address = Base58(00|PKHash|4checksumBytes)
```

## Example 2: From Transaction

### Given Data
```
PKHash: bcadb700c24da04b17feb9aa9bd71e368a4b623c
```

### Step 4: Add Version Byte
```
00bcadb700c24da04b17feb9aa9bd71e368a4b623c
```

### Steps 5-6: Double SHA-256
```
SHA256(SHA256(00|PKHash)):
dc40e08e9af8fd6bb0a8ea46839a96e871a9a5ef3aae91a4b4802c2076aaa1f2
```

### Step 7: Extract Checksum
```
Checksum: dc40e08e
```

### Step 8: Create Binary Address
```
00bcadb700c24da04b17feb9aa9bd71e368a4b623cdc40e08e
```

### Step 9: Base58 Encode
```
Final Address: 1JCe8z4jJVNXSjohjM4i9Hh813dLCNx2Sy
```

## Visual Flow

```
Private Key (32 bytes)
  ↓ ECDSA secp256k1
Public Key (65 bytes uncompressed)
  ↓ SHA-256
256-bit Hash (32 bytes)
  ↓ RIPEMD-160
160-bit Hash (20 bytes)
  ↓ Add version byte 0x00
Versioned Hash (21 bytes)
  ↓ SHA-256 twice
Checksum (first 4 bytes)
  ↓ Append to versioned hash
Binary Address (25 bytes)
  ↓ Base58 Encode
Bitcoin Address (26-35 chars)
```

## Tools and Verification

### Online Tools
- [Hash Calculator](http://www.fileformat.info/tool/hash.htm) - SHA-256 hashing
- [Bitcoin Tools](http://bitcoinvalued.com/tools.php) - HASH160 function
- [Base58 Converter](http://lenschulwitz.com/base58) - Base58 encoding

### Verification
To verify an address generation:
1. Use Base58Decode on final address
2. Check that decoded value = `00||PKHash||checksum`
3. Verify checksum = first 4 bytes of SHA256(SHA256(00||PKHash))
4. Verify PKHash = RIPEMD160(SHA256(PublicKey))

## References

### Bitcoin Wiki
- [Technical Background](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses#How_to_create_Bitcoin_Address)
- [P2PKH Script Validation](https://bitcoin.org/en/developer-guide#p2pkh-script-validation)

### Visual Guides
- [Address Creation Diagram](https://i.stack.imgur.com/AcXYt.png)

## Notes

- Addresses starting with '1' are standard P2PKH addresses
- Addresses starting with '3' are P2SH (multisig) addresses
- Addresses starting with 'bc1' are Bech32 (SegWit) addresses
- The same public key always produces the same address
- Different public keys virtually never produce the same address (collision resistance)

## Security Considerations

1. **Private key must be kept secret** - Anyone with the private key controls the funds
2. **Use cryptographically secure random number generator** for private key creation
3. **Never reuse addresses** - Generate new address for each transaction for privacy
4. **Verify checksums** - Always validate the 4-byte checksum before using an address
5. **Test with small amounts first** - Verify address generation is correct
