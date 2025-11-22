# Bitcoin Module

Bitcoin protocol implementation for educational purposes.

## Overview

This module implements Bitcoin's core functionality:
- **Keys & Addresses** - ECDSA key pairs, WIF format, address generation
- **Transactions** - Creation, signing, verification
- **Network** - P2P protocol, message handling
- **Mining** - Proof-of-work demonstration

**WARNING:** Educational only. No encryption, no fee calculation, connects to mainnet.

## Files

### Core Utilities

#### msgUtils.py ✓
**Bitcoin protocol and P2P message utilities**

Protocol utilities:
- Variable-length integer encoding (varint)
- Variable-length string encoding (varstr)
- Network address formatting
- Variable-length integer/string decoding

P2P message utilities:
- Create and parse protocol messages
- Version handshake
- Inventory (inv) messages
- Address (addr) messages
- Transaction broadcast

**Tests:** bitcoin/tests/test_msgUtils.py (2 tests)

### Address Generation

Generate Bitcoin addresses from private keys.

#### makeAddr.py
**Generate random Bitcoin address**

Creates new random private key and derives address:
```bash
python makeAddr.py
```

**Output:**
```
5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS  # WIF private key
1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T            # Bitcoin address
```

#### myWallet.py
**Generate address from specific private key**

```python
from bitcoin import myWallet
public_key = myWallet.createAddress('a2d43efac7e99b7e...')
```

**Tests:** bitcoin/tests/test_myWallet.py (4 tests)

### Transactions

Create and sign Bitcoin transactions.

#### txnUtils.py ✓
**Transaction utilities (library)**

Core transaction functions:
- `makeRawTransaction()` - Build unsigned transaction
- `makeSignedTransaction()` - Create and sign with ECDSA
- `verifyTxnSignature()` - Verify signature is valid
- ScriptSig and ScriptPubKey generation

**Tests:** bitcoin/tests/test_txnUtils.py (5 tests)

#### makeTransaction.py
**Create signed transaction (demo)**

Example showing full transaction flow:
```bash
python makeTransaction.py
```

**What it does:**
1. Loads private key from WIF
2. Creates transaction spending previous output
3. Signs with ECDSA
4. Verifies signature
5. Outputs raw hex (ready to broadcast)

**Edit before running:** Set your private key, previous TX hash, output amounts.

#### myTransaction.py
**Test 4 different RIPEMD-160 implementations**

Verifies all methods produce the same Bitcoin address:
```bash
python myTransaction.py
```

1. PyCrypto RIPEMD library
2. keyUtils library
3. Python hashlib
4. Custom `cryptography/ripemd160_educational.py`

Then runs rollback experiment.

### Network Protocol

Connect to Bitcoin P2P network and exchange messages.

**Protocol:** Port 8333, Magic `0xd9b4bef9`, Format: `[magic][command][length][checksum][payload]`

**Key functions in msgUtils.py:**
- `makeMessage()` - Format message with magic/checksum
- `getVersionMsg()` - Version handshake
- `getTxMsg()` - Transaction broadcast
- `getAddrMsg()` - Request peer addresses
- `processChunk()` - Parse received messages
- `varint()`, `varstr()` - Protocol encoding
- `processVarInt()`, `processVarStr()` - Protocol decoding

#### minimalPeerConnection.py
**Basic network connection (demo)**

Simplest example - connect and receive:
```bash
python minimalPeerConnection.py
```

Connects to Bitcoin node, sends version, prints "got packet" for responses.

#### minimalSendTxn.py
**Broadcast transaction (demo)**

Minimal transaction broadcast to mainnet:
```bash
python minimalSendTxn.py
```

**WARNING:** Broadcasts to mainnet!

#### sendBitcoinTransaction.py
**Advanced P2P communication (demo)**

Full protocol demonstration:
```bash
python sendBitcoinTransaction.py
```

- Version/verack handshake
- Requests peer addresses
- Parses and displays responses

### Mining

Demonstrate proof-of-work mining.

#### mine.py
**Find valid block hash**

```bash
python mine.py
```

Uses block 272784 (Jan 2014):
1. Calculate target from difficulty bits
2. Brute force nonce values
3. Find hash below target

**Fast because:** 2014 difficulty was much lower than today.

### Modified Versions

#### txnUtilsMod.py
Modified version of txnUtils.py - preserved for reference

## File Status

| File | Tests | Status | Description |
|------|-------|--------|-------------|
| msgUtils.py | 2 ✓ | Production | Protocol & P2P messages |
| txnUtils.py | 5 ✓ | Production | Transaction utils |
| myWallet.py | 4 ✓ | Working | Wallet functions |
| makeAddr.py | - | Working | Address generator |
| makeTransaction.py | - | Working | Transaction example |
| myTransaction.py | - | Working | Multi-method test |
| minimalPeerConnection.py | - | Working | Network demo |
| minimalSendTxn.py | - | Working | TX broadcast |
| sendBitcoinTransaction.py | - | Working | Advanced P2P |
| mine.py | - | Working | Mining demo |
| txnUtilsMod.py | - | Archive | Modified version |

**Total:** 11 tests passing

## Testing

Run all tests:
```bash
cd bitcoin/tests

python test_msgUtils.py     # 2 tests - Protocol & P2P messages
python test_txnUtils.py     # 5 tests - Transaction utils
python test_myWallet.py     # 4 tests - Wallet functions
```

**Note:** Base58 encoding tests are in `cryptography/tests/test_base58Utils.py`

## Python Version

**Requires Python 2.7**

The code uses Python 2 syntax:
- `print` statements (not functions)
- `.encode('hex')` / `.decode('hex')`
- String/bytes handling

**Dependencies:**
```bash
pip install ecdsa
```

Optional:
```bash
pip install pycrypto  # For comparison in myTransaction.py
```

## Security Warning

**DO NOT USE FOR REAL BITCOIN**

This is educational code:
- No key encryption
- No secure storage
- No fee calculation
- Minimal error handling
- Connects to mainnet
- No production testing

**For real Bitcoin use:**
- Bitcoin Core
- python-bitcoinlib
- Hardware wallets
- Production-tested software

## Bitcoin Concepts

### Keys and Addresses

```
Private Key (256 bits)
  ↓ ECDSA (secp256k1)
Public Key (512 bits)
  ↓ SHA-256
256-bit hash
  ↓ RIPEMD-160
160-bit hash (Hash160)
  ↓ Base58Check
Bitcoin Address
```

### Transactions

```
Version (4 bytes)
Input Count (varint)
Inputs []
  - Previous TX hash (32 bytes)
  - Output index (4 bytes)
  - ScriptSig length (varint)
  - ScriptSig (signature + pubkey)
  - Sequence (4 bytes)
Output Count (varint)
Outputs []
  - Value in satoshis (8 bytes)
  - ScriptPubKey length (varint)
  - ScriptPubKey (script)
Locktime (4 bytes)
```

### P2P Protocol

**Message Format:**
```
Magic (4 bytes): 0xd9b4bef9
Command (12 bytes): "version\0\0\0\0\0"
Length (4 bytes)
Checksum (4 bytes): first 4 bytes of SHA256(SHA256(payload))
Payload (variable)
```

**Port:** 8333 (mainnet)

## Common Tasks

### Generate Address
```python
from bitcoin import myWallet
public_key = myWallet.createAddress('a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f')
```

### Create Transaction
```python
from bitcoin import txnUtils, keyUtils

signed_txn = txnUtils.makeSignedTransaction(
    privateKey,
    outputTxHash,
    sourceIndex,
    scriptPubKey,
    outputs
)
```

### Verify Signature
```python
from bitcoin import txnUtils

txnUtils.verifyTxnSignature(signed_txn_hex)
```

### Convert WIF
```python
from cryptography import keyUtils

# To WIF
wif = keyUtils.privateKeyToWif(private_key_hex)

# From WIF
key = keyUtils.wifToPrivateKey(wif)
```

### Encode Bitcoin protocol data
```python
from bitcoin import msgUtils

# Variable-length integer
varint_data = msgUtils.varint(1000)

# Variable-length string
varstr_data = msgUtils.varstr(b'hello')

# Network address
addr = msgUtils.netaddr(socket.inet_aton("127.0.0.1"), 8333)
```

## References

- [Bitcoin Protocol Specification](https://en.bitcoin.it/wiki/Protocol_documentation)
- [Bitcoin Developer Reference](https://bitcoin.org/en/developer-reference)
- [Bitcoins the hard way](http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html)
- [Base58Check encoding](https://en.bitcoin.it/wiki/Base58Check_encoding)
- [Script](https://en.bitcoin.it/wiki/Script)
