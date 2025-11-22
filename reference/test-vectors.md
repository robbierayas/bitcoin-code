# Bitcoin Test Vectors and Examples

Complete examples for testing Bitcoin address generation and transaction signing.

## Test Case 1: Complete Address Generation

### Private Key
```
a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f
```

### Public Key (Uncompressed)
```
0427d64b2de9f51ac1bf6b287088de3afcf67e8dd820848128cc27f71c18c5f8ba
efe71cc14052b4989e33a17f4795022f70313561cb3ef3d0b599c49933daa6fd
```

**Format:** 65 bytes
- Prefix: `04`
- X coordinate: `27d64b2de9f51ac1bf6b287088de3afcf67e8dd820848128cc27f71c18c5f8ba`
- Y coordinate: `efe71cc14052b4989e33a17f4795022f70313561cb3ef3d0b599c49933daa6fd`

### Step 1: SHA-256 of Public Key
```
Input:  0427d64b2de9f51ac1bf6b287088de3afcf67e8dd820848128cc27f71c18c5f8ba
        efe71cc14052b4989e33a17f4795022f70313561cb3ef3d0b599c49933daa6fd

Output: f6c4d6736f912ffebe65fb1497aac2a111d037883f39b5d72ea0d39f216ed368
```

**Tool:** [Hash Calculator](http://www.fileformat.info/tool/hash.htm)

### Step 2: RIPEMD-160 of SHA-256 Result
```
Input:  f6c4d6736f912ffebe65fb1497aac2a111d037883f39b5d72ea0d39f216ed368

Output: f3cd5ddd30ad4d28f13cf195786f2e95e8914b22
```

**Verification Method:**
Using [Bitcoin Tools](http://bitcoinvalued.com/tools.php) HASH160 function:
```
Base58Decode(HASH160).toLowerCase() = 00||RIPEMD160(SHA256(PK)) - last4bytes
```

### Step 3: Add Version Byte
```
Version: 00 (Mainnet)
Result:  00f3cd5ddd30ad4d28f13cf195786f2e95e8914b22
```

### Step 4: First SHA-256 (for checksum)
```
Input:  00f3cd5ddd30ad4d28f13cf195786f2e95e8914b22

Output: 9c618e84ba7bb0b6d208f7f57d9b92bdfb929efba53a3668469115a96105db90
```

### Step 5: Second SHA-256 (for checksum)
```
Input:  9c618e84ba7bb0b6d208f7f57d9b92bdfb929efba53a3668469115a96105db90

Output: 5c8492ba9c962bd90185764df1d68e106828d9608ebd42a81280e3d7ba7f41f7
```

### Step 6: Extract Checksum
```
Checksum (first 4 bytes): 5c8492ba
```

### Step 7: Binary Address
```
25-byte address: 00f3cd5ddd30ad4d28f13cf195786f2e95e8914b225c8492ba
```

**Format:** version(1) + hash160(20) + checksum(4) = 25 bytes

### Step 8: Base58 Encoding
```
Input:  00f3cd5ddd30ad4d28f13cf195786f2e95e8914b225c8492ba

Output: 1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
```

**Tool:** [Base58 Converter](http://lenschulwitz.com/base58)

### ✓ Final Address
```
1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
```

## Test Case 2: From Transaction Example

### Given: Public Key Hash
```
PKHash: bcadb700c24da04b17feb9aa9bd71e368a4b623c
```

### Step 1: Add Version Byte
```
Versioned: 00bcadb700c24da04b17feb9aa9bd71e368a4b623c
```

### Step 2: First SHA-256
```
Input:  00bcadb700c24da04b17feb9aa9bd71e368a4b623c

(Output not shown in original, compute for verification)
```

### Step 3: Second SHA-256 (for checksum)
```
Output: dc40e08e9af8fd6bb0a8ea46839a96e871a9a5ef3aae91a4b4802c2076aaa1f2
```

### Step 4: Extract Checksum
```
Checksum (first 4 bytes): dc40e08e
```

### Step 5: Binary Address
```
25-byte address: 00bcadb700c24da04b17feb9aa9bd71e368a4b623cdc40e08e
```

### Step 6: Base58 Encoding
```
Output: 1JCe8z4jJVNXSjohjM4i9Hh813dLCNx2Sy
```

### ✓ Final Address
```
1JCe8z4jJVNXSjohjM4i9Hh813dLCNx2Sy
```

### Associated scriptPubKey
```
76a914bcadb700c24da04b17feb9aa9bd71e368a4b623c88ac
```

**Decoded:**
- `76` - OP_DUP
- `a9` - OP_HASH160
- `14` - Push 20 bytes
- `bcadb700c24da04b17feb9aa9bd71e368a4b623c` - PKHash
- `88` - OP_EQUALVERIFY
- `ac` - OP_CHECKSIG

This is a standard P2PKH (Pay-to-PubKey-Hash) output script.

## Transaction Example

### Real Transaction on Blockchain

**Transaction ID:**
```
99dbfd52265ee86d46d3802d2ee2cdf70600896d8fa923c5f5236abe17231339
```

**Explorer Link:**
```
https://chainquery.com/bitcoin-api/getrawtransaction/
99dbfd52265ee86d46d3802d2ee2cdf70600896d8fa923c5f5236abe17231339/1
```

Use this to verify:
- Transaction structure
- Signature format
- Input/output scripts
- Hash calculations

## Verification Checklist

### For Address Generation

- [ ] Private key is 32 bytes (64 hex characters)
- [ ] Public key is 65 bytes uncompressed or 33 bytes compressed
- [ ] SHA-256 hash is 32 bytes
- [ ] RIPEMD-160 hash is 20 bytes
- [ ] Version byte is correct (0x00 for mainnet, 0x6F for testnet)
- [ ] Checksum is first 4 bytes of double SHA-256
- [ ] Binary address is 25 bytes total
- [ ] Base58 encoding produces valid address format

### For Signature Verification

- [ ] Message hash is double SHA-256
- [ ] Signature is in valid DER format
- [ ] r and s are in range [1, n-1]
- [ ] Public key is on the secp256k1 curve
- [ ] Verification equation holds: r ≡ x₁ (mod n)

## Online Testing Tools

### Hash Functions
- [Hash Calculator](http://www.fileformat.info/tool/hash.htm)
  - SHA-256 calculation
  - SHA-1, MD5, and others

### Bitcoin Tools
- [Bitcoin Valued Tools](http://bitcoinvalued.com/tools.php)
  - HASH160 function (SHA256 + RIPEMD160)
  - Base58 decode
  - Address validation

### Base58 Encoding
- [Len Schulwitz Base58](http://lenschulwitz.com/base58)
  - Encode/decode Base58
  - Base58Check encoding

### ECDSA Testing
- [jsrsasign ECDSA Sample](https://kjur.github.io/jsrsasign/sample-ecdsa.html)
  - Generate key pairs
  - Sign messages
  - Verify signatures

## Manual Verification Example

### Verify Test Case 1 Step-by-Step

```python
import hashlib

# Step 1: Define public key
pubkey = "0427d64b2de9f51ac1bf6b287088de3afcf67e8dd820848128cc27f71c18c5f8baefe71cc14052b4989e33a17f4795022f70313561cb3ef3d0b599c49933daa6fd"

# Step 2: SHA-256 of public key
sha256_hash = hashlib.sha256(bytes.fromhex(pubkey)).hexdigest()
print(f"SHA256: {sha256_hash}")
# Expected: f6c4d6736f912ffebe65fb1497aac2a111d037883f39b5d72ea0d39f216ed368

# Step 3: RIPEMD-160 of SHA-256 result
ripemd160 = hashlib.new('ripemd160')
ripemd160.update(bytes.fromhex(sha256_hash))
hash160 = ripemd160.hexdigest()
print(f"RIPEMD160: {hash160}")
# Expected: f3cd5ddd30ad4d28f13cf195786f2e95e8914b22

# Step 4: Add version byte
versioned = "00" + hash160
print(f"Versioned: {versioned}")

# Step 5-6: Double SHA-256 for checksum
checksum_full = hashlib.sha256(hashlib.sha256(bytes.fromhex(versioned)).digest()).hexdigest()
checksum = checksum_full[:8]  # First 4 bytes
print(f"Checksum: {checksum}")
# Expected: 5c8492ba

# Step 7: Create binary address
binary_addr = versioned + checksum
print(f"Binary: {binary_addr}")
# Expected: 00f3cd5ddd30ad4d28f13cf195786f2e95e8914b225c8492ba

# Step 8: Base58 encode (requires base58 library)
# import base58
# address = base58.b58encode(bytes.fromhex(binary_addr)).decode()
# print(f"Address: {address}")
# Expected: 1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
```

## Common Test Errors

### Wrong SHA-256 Output
**Problem:** Hash doesn't match expected value
**Solution:**
- Ensure input is exactly 65 bytes for uncompressed key
- Include the 0x04 prefix
- Check for any whitespace or newlines in input

### Wrong RIPEMD-160 Output
**Problem:** Hash160 doesn't match
**Solution:**
- Input must be the SHA-256 hash (32 bytes), not the public key
- Use hexadecimal input, not Base58

### Wrong Checksum
**Problem:** Checksum doesn't match
**Solution:**
- Perform SHA-256 twice (not once)
- Take first 4 bytes (8 hex characters)
- Input is version byte + hash160 (21 bytes total)

### Wrong Base58 Output
**Problem:** Address doesn't match
**Solution:**
- Ensure 25-byte input (version + hash + checksum)
- Leading zeros must be preserved as '1' characters in Base58
- Use Base58Check encoding, not standard Base58

## Extended Test Vectors

### Bitcoin Wiki Examples

See also:
- [Bitcoin Address Examples](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses)
- [Transaction Malleability Test Cases](https://en.bitcoin.it/wiki/Transaction_Malleability)

### Dormant Addresses Research

For studying old/dormant addresses:
- [Dormant Addresses Spreadsheet](https://docs.google.com/spreadsheets/d/1xTROekDerP1TPOB3SOD_1bbQr580BPqbhF3YHdO96pw/edit#gid=189298223)

Contains addresses with:
- Large balances
- No recent activity
- Historical significance
- Educational value for analysis

## References

### Stack Exchange
- [What goes into the message of a transaction signature?](http://bitcoin.stackexchange.com/questions/37093/what-goes-in-to-the-message-of-a-transaction-signature)

### Research Questions
- [Reverse SHA?](http://stackoverflow.com/questions/11937192/sha-256-pseuedocode)
  - Why SHA-256 cannot be reversed
  - Rainbow tables and preimage attacks
