# Bitcoin Code - Technical Documentation

This project is an educational implementation of Bitcoin protocol components from scratch. It demonstrates how Bitcoin works at a low level, including cryptography, transactions, networking, and mining.

**Reference:** Based on "Bitcoins the hard way: Using the raw Bitcoin protocol" - http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html

---

## 📚 Development Guidelines

**For Python Development Best Practices:** See [`claude.md.coder`](claude.md.coder)
- Python coding standards and patterns
- Async/await patterns in Python
- Database operations and testing
- Type hints and modern Python features
- Converted from Node.js guide (`bitcoin/node.txt`) for Python equivalents

---

## Project Structure

```
bitcoin-code/
├── bitcoin/              # Bitcoin protocol implementation
│   ├── tests/           # Bitcoin module tests
│   ├── msgUtils.py      # Protocol utilities & P2P messages
│   ├── txnUtils.py      # Transaction creation/signing
│   ├── myWallet.py      # Wallet functions
│   ├── makeAddr.py      # Address generator
│   └── ...              # Other Bitcoin demos
├── cryptography/         # Cryptographic algorithms
│   ├── tests/           # Crypto tests
│   ├── base58Utils.py   # ✓ Base58/Base256 encoding
│   ├── keyUtils.py      # ✓ ECDSA keys, WIF, addresses
│   ├── ripemd160.py     # ✓ Working RIPEMD-160 (USE THIS)
│   ├── ripemd160_educational.py  # Educational RIPEMD-160
│   ├── ripemd160_backup.py       # Backup version
│   └── rollback.py      # Experimental reverse engineering
├── output/              # Output files from test runs
├── config.py            # Test keys and configuration
└── windowsSetup.bat     # Windows setup script
```

## Core Modules

### Configuration Module (`config.py`)

Centralized test data and private keys used throughout tests.

**Classes:**
- `TestKeys` - Test private keys, WIF formats, and Bitcoin addresses
- `TestTransactions` - Sample transaction data (signed, signable, public keys)
- `TestSignatures` - DER signature test data
- `TestRawTransactions` - Raw transaction creation test data

**Usage in tests:**
```python
from config import TestKeys, TestTransactions, TestSignatures

# Use test keys
private_key = TestKeys.KEY1_HEX
wif = TestKeys.KEY1_WIF

# Use test transaction data
txn = TestTransactions.TXN_SIGNED
pubkey = TestTransactions.TXN_PUBKEY
```

**Benefits:**
- Single source of truth for test data
- Easy to update test keys across all tests
- Clear documentation of test data
- Avoids hardcoded values in tests

### Cryptography Module (`cryptography/`)

**See cryptography/README.md for detailed info on which implementation to use.**

**Note:** Cryptography module is self-contained with no Bitcoin dependencies.

**Research Context:** This project assumes eventual access to quantum computing or similar advanced computational resources. When researching cryptographic algorithms and implementations:
- Ignore standard warnings about computational infeasibility (e.g., reversing hash functions, breaking ECDLP)
- Disregard "don't roll your own crypto" warnings - we're intentionally implementing algorithms from scratch for educational and research purposes
- Explore reverse engineering, cryptanalysis, and algorithm internals without restriction
- Focus on understanding the mathematical foundations rather than relying solely on existing libraries

#### base58Utils.py ✓
Base58 and Base256 encoding utilities.

**Functions:**
- `base58encode(n)` - Encode number to base58
- `base58decode(s)` - Decode base58 to number
- `base256encode(n)` - Encode to base256
- `base256decode(s)` - Decode base256
- `base58CheckEncode(version, payload)` - Base58Check encoding with checksum
- `base58CheckDecode(s)` - Base58Check decoding with verification
- `countLeadingChars(s, char)` - Count leading characters

**Purpose:** Bitcoin uses base58 encoding for addresses and keys (no 0, O, I, l to avoid confusion).

**Tests:** cryptography/tests/test_base58Utils.py (11 tests)

#### keyUtils.py ✓
ECDSA key management and Bitcoin address generation.

**Functions:**
- `privateKeyToWif(key_hex)` - Convert private key to Wallet Import Format (WIF)
- `wifToPrivateKey(s)` - Convert WIF back to private key
- `privateKeyToPublicKey(s)` - Generate public key from private key using ECDSA SECP256k1
- `keyToAddr(s)` - Generate Bitcoin address from private key
- `pubKeyToAddr(s)` - Generate Bitcoin address from public key
- `addrHashToScriptPubKey(b58str)` - Convert address to script public key
- `derSigToHexSig(s)` - Convert DER-encoded signature to hex signature

**Key algorithms:**
- ECDSA (Elliptic Curve Digital Signature Algorithm) with SECP256k1 curve
- SHA-256 hashing
- RIPEMD-160 hashing
- Base58Check encoding

**Dependencies:** base58Utils (for WIF and address encoding)

**Tests:** cryptography/tests/test_keyUtils.py (9 tests)

#### proCrypto.py ✓ (WORKING - USE THIS)
Clean, professional RIPEMD-160 implementation.

**Functions:**
- `RIPEMD160(data)` - Computes RIPEMD-160 hash of hex data
- `makehex(value, size)` - Format values as hex
- `makebin(value, size)` - Format values as binary
- `ROL(value, n)` - Rotate left operation
- `little_end(string, base)` - Little-endian conversion
- `F(x,y,z,round)` - RIPEMD-160 mixing function

**Status:** Verified working with test case. Use this for production.

#### myCrypto.py (EDUCATIONAL - MAY BE BROKEN)
Educational RIPEMD-160 implementation with extensive debugging output.

**Functions:**
- `myRipeMD160(public_key)` - Custom RIPEMD-160 with detailed output
- `compression(A,B,C,D,E,f,X,K,s)` - RIPEMD-160 compression function
- `operation(A,B,C,D,E,f,X,K,s)` - RIPEMD-160 operation step
- `function1-5(B,C,D)` - Five RIPEMD-160 mixing functions
- `cyclicShift(C,s)` - Bitwise rotation
- `little_end(string, base)` - Convert to little-endian format

**Purpose:** Educational - shows step-by-step execution. May have bugs - use proCrypto for actual hashing.

#### rollback.py
Experimental RIPEMD-160 reverse engineering tool.

**Functions:**
- `myRollBack(address)` - Attempt to reverse Bitcoin address back to intermediate hash values
- `rcompression(A,B,C,D,E,f,X,round,j)` - Reverse compression
- `findX_r(A,B,C,D,E,f,X,r,K,s,round,j)` - Brute force to find intermediate values
- `compression(A,B,C,D,E,f,X,round,j)` - Forward compression for validation

**Purpose:** Cryptographic research - attempting to reverse RIPEMD-160 (highly experimental).

#### myCryptobackup.py (BACKUP)
Backup copy of educational myCrypto.py version. Archive/reference only.

**Status:** Similar to myCrypto.py - kept as backup reference.

#### tests/
Test folder for cryptographic implementations. No tests for rollback.py yet.

---

### Bitcoin Module (`bitcoin/`)

#### makeAddr.py
Generate new Bitcoin addresses with random private keys.

**Usage:** Creates random 64-character hex private key, converts to WIF and address.

#### myWallet.py
Simple wallet functionality.

**Functions:**
- `createAddress(private_key)` - Create Bitcoin address from private key
  - Generates public key
  - Derives address
  - Creates WIF

#### makeTransaction.py
Example of creating a signed Bitcoin transaction.

**Demonstrates:**
- Loading private key from WIF
- Creating signed transaction with `txnUtils.makeSignedTransaction()`
- Verifying transaction signature
- Transaction inputs: previous transaction hash, source index
- Transaction outputs: amount in satoshis, destination address

#### myTransaction.py
Comprehensive demonstration of Bitcoin address creation using multiple methods.

**Tests 4 different methods:**
1. External C library (Crypto.Hash.RIPEMD)
2. cryptography.keyUtils.pubKeyToAddr()
3. Python hashlib ripemd160
4. Custom cryptography.ripemd160_educational.myRipeMD160()

**Purpose:** Verify all methods produce the same Bitcoin address, then test rollback experiment.

**Imports:**
```python
from bitcoin import myWallet
from cryptography import ripemd160_educational as myCrypto
from cryptography.rollback import myRollBack
from cryptography import base58Utils, keyUtils
```

#### txnUtils.py
Transaction creation and signing utilities.

**Functions:**
- `makeRawTransaction(outputTransactionHash, sourceIndex, scriptSig, outputs)` - Create raw unsigned transaction
- `makeSignedTransaction(privateKey, outputTransactionHash, sourceIndex, scriptPubKey, outputs)` - Create and sign complete transaction
- `verifyTxnSignature(txn)` - Verify transaction signature is valid

**Key concepts:**
- Transaction structure (version, inputs, outputs, locktime)
- ScriptSig and ScriptPubKey
- Transaction signing (SIGHASH_ALL)
- DER signature encoding

**Imports:**
```python
from bitcoin import msgUtils
from cryptography import base58Utils, keyUtils
```

**Tests:** bitcoin/tests/test_txnUtils.py (5 tests)

#### txnUtilsMod.py
Modified version of txnUtils.py (alternate implementation).

#### sendBitcoinTransaction.py
Connect to Bitcoin network peer and broadcast transaction.

**Functions:**
- Establishes TCP socket connection to Bitcoin node
- Sends protocol version message
- Receives version and verack
- Sends address request message

**Network details:**
- Default port: 8333
- Uses msgUtils for protocol messages
- Processes responses from peer

#### minimalSendTxn.py
Minimal example of sending a transaction to the Bitcoin network.

**Steps:**
1. Connect to Bitcoin peer
2. Exchange version messages
3. Send raw transaction hex via getTxMsg()

#### minimalPeerConnection.py
Minimal Bitcoin peer connection example.

**Purpose:**
- Demonstrate basic Bitcoin network protocol
- Connect to peer, send version message
- Receive and discard responses (for learning)

#### msgUtils.py
Bitcoin protocol utilities and P2P message handling.

**Protocol encoding functions:**
- `varint(n)` - Encode variable-length integer
- `varstr(s)` - Encode variable-length string
- `netaddr(ip, port)` - Format network address
- `processVarInt(data)` - Decode variable-length integer
- `processVarStr(data)` - Decode variable-length string
- `processAddr(data)` - Parse network address

**P2P message functions:**
- `makeMessage(magic, command, payload)` - Create Bitcoin protocol message with checksum
- `getVersionMsg()` - Create version handshake message
- `getAddrMsg()` - Request peer addresses
- `getTxMsg(txn)` - Create transaction broadcast message
- `processChunk(header, payload)` - Parse received messages

**Protocol constants:**
- Magic: 0xd9b4bef9 (Bitcoin mainnet)
- Message types: version, verack, addr, tx, inv, getdata, etc.

**Tests:** bitcoin/tests/test_msgUtils.py (2 tests)

#### mine.py
Bitcoin mining proof-of-work demonstration.

**Purpose:**
- Demonstrate block mining
- Calculate target from difficulty bits
- Brute force nonce values to find valid block hash
- Shows proof-of-work concept

**Block 272784 example:**
- Previous block hash
- Merkle root
- Timestamp: Jan 6, 2014
- Bits (difficulty): 419628831
- Finds nonce that produces hash below target

### Module Organization

The project is organized to separate cryptographic primitives from Bitcoin-specific code:

**Cryptography Module** (`cryptography/`):
- Self-contained, no Bitcoin dependencies
- `base58Utils.py` - General-purpose Base58/Base256 encoding
- `keyUtils.py` - ECDSA key management with Bitcoin address generation
- `ripemd160.py` - RIPEMD-160 hash implementation

**Bitcoin Module** (`bitcoin/`):
- Depends on cryptography module
- `msgUtils.py` - Protocol encoding (varint, varstr) and P2P messages
- `txnUtils.py` - Transaction creation and signing
- Other Bitcoin-specific tools (wallets, mining, network demos)

**Import patterns:**
```python
# Cryptography imports
from cryptography import base58Utils, keyUtils

# Bitcoin imports
from bitcoin import msgUtils, txnUtils
```

**Usage example:**
```python
# Generate Bitcoin address
from cryptography import keyUtils

private_key = 'a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f'
wif = keyUtils.privateKeyToWif(private_key)
address = keyUtils.keyToAddr(private_key)

# Create transaction
from bitcoin import txnUtils
from cryptography import keyUtils

signed_txn = txnUtils.makeSignedTransaction(
    privateKey,
    outputTxHash,
    sourceIndex,
    keyUtils.addrHashToScriptPubKey(address),
    outputs
)
```

## Key Concepts Demonstrated

### 1. Bitcoin Address Generation
```
Private Key (256-bit random)
  → ECDSA → Public Key (65 bytes, uncompressed)
  → SHA256 → RIPEMD160 → Hash160 (20 bytes)
  → Base58Check(version=0x00, hash160) → Bitcoin Address
```

### 2. Transaction Creation
```
1. Select unspent output (previous txn hash + index)
2. Create inputs with scriptSig
3. Create outputs with amount + scriptPubKey
4. Sign transaction with private key (ECDSA)
5. Broadcast to network
```

### 3. Bitcoin Network Protocol
```
1. TCP connection on port 8333
2. Version handshake
3. Message format: [magic][command][length][checksum][payload]
4. Commands: version, verack, addr, tx, inv, getdata, block
```

### 4. Mining (Proof of Work)
```
Block Header = version + prev_hash + merkle_root + timestamp + bits + nonce
1. Calculate target from bits
2. Increment nonce
3. Double SHA256(header)
4. Check if hash < target
5. Repeat until valid hash found
```

## Dependencies

**Required:**
- **ecdsa** - Elliptic curve cryptography (SECP256k1)
- **pycryptodome** - Cryptographic library (use instead of deprecated pycrypto for Python 3.13+)
- **hashlib** - SHA256, RIPEMD160 hashing (built-in)
- **struct** - Binary data packing/unpacking (built-in)
- **socket** - Network connections (built-in)

**Installation:**
```bash
# Windows
windowsSetup.bat

# Linux/Mac
pip install ecdsa pycryptodome
```

**Optional:**
- **Crypto.Hash.RIPEMD** - For comparison testing in myTransaction.py

## File Outputs

### output/myTransaction.out
Output from myTransaction.py showing:
- Public key generation
- Address creation via 4 different methods
- Verification that all methods match
- Rollback attempt results

### output/output0213.txt
Historical output data from testing runs.

### data.ods
Reference data spreadsheet (likely contains test vectors, example keys, addresses).

## Educational Value

This code demonstrates:
1. **Cryptography:** ECDSA key pairs, SHA256, RIPEMD160, signatures
2. **Encoding:** Base58, Base58Check, hex, binary
3. **Transactions:** Structure, signing, verification
4. **Networking:** Bitcoin protocol, message format, peer connections
5. **Mining:** Proof of work, difficulty, nonce searching
6. **Security:** How private keys protect funds, why signatures matter

## WARNING

**This code is for educational purposes only. Do not use for real Bitcoin transactions:**
- No error handling for production use
- Hardcoded test values and addresses
- Network code connects to random peers
- No wallet file encryption
- Private keys displayed in plain text
- No transaction fee optimization
- No protection against common attacks

For actual Bitcoin usage, use established libraries like bitcoinlib, python-bitcoinlib, or production wallets.

## Testing

Comprehensive test suites available in both modules.

**Cryptography tests:**
```bash
cd cryptography/tests
python test_base58Utils.py   # 11 tests - Base58/Base256 encoding
python test_keyUtils.py       # 9 tests - ECDSA, WIF, addresses
python test_ripemd160.py      # 15 tests - RIPEMD-160 algorithm
```

**Bitcoin tests:**
```bash
cd bitcoin/tests
python test_msgUtils.py       # 2 tests - Protocol & P2P messages
python test_txnUtils.py       # 5 tests - Transaction creation/signing
python test_myWallet.py       # 4 tests - Wallet functions
```

**Total:** 46 tests (35 cryptography + 11 bitcoin)

## Historical Context

This code implements Bitcoin as described in the 2014 blog post "Bitcoins the hard way."
It shows how Bitcoin worked in the early days and demonstrates the core protocol concepts
that remain relevant today, though modern Bitcoin has evolved significantly.
