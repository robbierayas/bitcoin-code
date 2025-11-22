# BIP39 Mnemonic Seed Phrase Implementation

This module implements BIP39 (Bitcoin Improvement Proposal 39) mnemonic seed phrase functionality for generating Bitcoin wallets from human-readable word sequences.

## What is BIP39?

BIP39 defines how to generate a deterministic Bitcoin wallet from a mnemonic seed phrase (typically 12, 15, 18, 21, or 24 words). This allows users to backup and restore their entire wallet using just those words.

## Features

- Convert mnemonic phrases to seeds using PBKDF2-HMAC-SHA512
- Derive BIP32 master private keys from seeds
- Optional passphrase support for additional security
- Full Unicode normalization (NFKD) support
- Deterministic key generation

## Usage

### Method 1: Quick Wallet Generation

```python
from cryptography import bip39

mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
wallet = bip39.mnemonic_to_wallet(mnemonic)

print(wallet['address'])      # Bitcoin address
print(wallet['private_key'])  # Private key (hex)
print(wallet['wif'])          # Wallet Import Format
print(wallet['public_key'])   # Public key (hex)
print(wallet['chain_code'])   # BIP32 chain code for HD derivation
```

### Method 2: Using KeyPair Class

```python
from cryptography.keypair import KeyPair

mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
keypair = KeyPair.from_mnemonic(mnemonic)

address = keypair.get_address()
wif = keypair.to_wif()
```

### Method 3: With Optional Passphrase

```python
from cryptography.keypair import KeyPair

mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
passphrase = "my_secret_passphrase"

# Different passphrase = different wallet
keypair = KeyPair.from_mnemonic(mnemonic, passphrase)
```

### Method 4: Step-by-Step Conversion

```python
from cryptography import bip39
from cryptography.keypair import KeyPair

mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"

# Step 1: Mnemonic -> Seed (64 bytes)
seed = bip39.mnemonic_to_seed(mnemonic)

# Step 2: Seed -> Master Key (BIP32)
private_key_hex, chain_code = bip39.seed_to_master_key(seed)

# Step 3: Create KeyPair from private key
keypair = KeyPair(private_key_hex)
```

## API Reference

### `mnemonic_to_seed(mnemonic, passphrase="")`

Convert BIP39 mnemonic phrase to 64-byte seed using PBKDF2-HMAC-SHA512.

**Parameters:**
- `mnemonic` (str): Space-separated mnemonic words
- `passphrase` (str): Optional passphrase (default: "")

**Returns:**
- bytes: 64-byte seed

**Example:**
```python
seed = bip39.mnemonic_to_seed("word1 word2 word3 ...")
```

### `seed_to_master_key(seed)`

Convert BIP39 seed to BIP32 master private key using HMAC-SHA512 with "Bitcoin seed".

**Parameters:**
- `seed` (bytes): 64-byte seed from `mnemonic_to_seed()`

**Returns:**
- tuple: (master_private_key_hex, chain_code_hex)
  - `master_private_key_hex`: 32-byte private key as hex string
  - `chain_code_hex`: 32-byte chain code as hex string

**Example:**
```python
private_key, chain_code = bip39.seed_to_master_key(seed)
```

### `mnemonic_to_private_key(mnemonic, passphrase="")`

Convenience function to convert mnemonic directly to private key.

**Parameters:**
- `mnemonic` (str): Space-separated mnemonic words
- `passphrase` (str): Optional passphrase (default: "")

**Returns:**
- str: 32-byte private key as hex string (64 characters)

**Example:**
```python
private_key = bip39.mnemonic_to_private_key(mnemonic)
```

### `mnemonic_to_wallet(mnemonic, passphrase="")`

Generate complete wallet information from mnemonic.

**Parameters:**
- `mnemonic` (str): Space-separated mnemonic words
- `passphrase` (str): Optional passphrase (default: "")

**Returns:**
- dict: Wallet information with keys:
  - `'private_key'`: hex private key
  - `'wif'`: Wallet Import Format
  - `'address'`: Bitcoin address
  - `'public_key'`: hex public key
  - `'chain_code'`: hex chain code (for HD derivation)

**Example:**
```python
wallet = bip39.mnemonic_to_wallet(mnemonic)
```

### `KeyPair.from_mnemonic(mnemonic, passphrase="")`

Class method to create KeyPair instance from BIP39 mnemonic.

**Parameters:**
- `mnemonic` (str): Space-separated mnemonic words
- `passphrase` (str): Optional passphrase (default: "")

**Returns:**
- KeyPair: New KeyPair instance derived from mnemonic

**Example:**
```python
keypair = KeyPair.from_mnemonic(mnemonic)
```

## Technical Details

### BIP39 Process

1. **Input**: Mnemonic phrase (12-24 words) + optional passphrase
2. **Unicode Normalization**: Apply NFKD normalization to mnemonic and passphrase
3. **PBKDF2**:
   - Hash function: HMAC-SHA512
   - Password: mnemonic (normalized)
   - Salt: "mnemonic" + passphrase (normalized)
   - Iterations: 2048
   - Output: 64 bytes (512 bits)
4. **Output**: 64-byte seed

### BIP32 Master Key Derivation

1. **Input**: 64-byte BIP39 seed
2. **HMAC-SHA512**:
   - Key: "Bitcoin seed" (UTF-8 bytes)
   - Data: seed
3. **Output**:
   - Left 32 bytes: Master private key
   - Right 32 bytes: Master chain code (for HD wallet derivation)

### Standards Compliance

- BIP39: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- BIP32: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
- Uses official test vectors for validation

## Test Example

Your provided seed phrase generates:

```
Mnemonic:     grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy
Private Key:  f812d57153e18ade09891e30568e9048626f7363be2ac350a9e380bab5c09936
WIF:          5KhYHeiG8vXZ26hJST45F7D19mycC3LUewJEa8Ea5QEyQoVxUdz
Address:      1Ciu4hsUJwyeGCBsoyVPiURgQ6XFvTWGF4
Public Key:   045218a05c2b35922d067891b9b0796736ca426b...
Chain Code:   3a62447ed2a9544c79bb61987e0f0af5b0a379792c38bf2c150ea8fecc1c01ca
```

## Testing

Run comprehensive test suite:

```bash
python cryptography/tests/test_bip39.py
```

**Test Coverage:**
- 19 tests covering all functionality
- Official BIP39 test vector validation
- Deterministic output verification
- Passphrase support testing
- Unicode handling
- Edge cases

## Security Notes

1. **Mnemonic Security**: Your seed phrase is the master key to your wallet. Anyone with the phrase can access your funds.

2. **Passphrase**: Optional but recommended. Acts as a 25th word. Different passphrases produce completely different wallets from the same mnemonic.

3. **Deterministic**: Same mnemonic + passphrase always produces the same wallet. This is a feature, not a bug.

4. **Educational Use**: This implementation is for educational purposes. For production use, consider established libraries like `python-mnemonic` or hardware wallets.

## Example Script

See `examples/generate_from_seed_phrase.py` for a complete working example demonstrating all usage methods.

## Dependencies

- `hashlib` (built-in): PBKDF2, SHA-512
- `hmac` (built-in): HMAC operations
- `unicodedata` (built-in): Unicode normalization
- `ecdsa`: Elliptic curve cryptography (SECP256k1)

## File Structure

```
cryptography/
├── bip39.py                    # BIP39 implementation
├── keypair.py                  # KeyPair class with from_mnemonic() method
├── tests/
│   └── test_bip39.py          # Comprehensive test suite (19 tests)
└── BIP39_README.md            # This file

examples/
└── generate_from_seed_phrase.py  # Usage examples
```
