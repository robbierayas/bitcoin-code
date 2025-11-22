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

#### wallet.py ✓ (NEW - OBJECT ORIENTED)
**Bitcoin wallet class for key and transaction management**

Object-oriented wallet with keypair encapsulation.

**Class: Wallet**
- `keypair` - KeyPair instance (public attribute)
- Constructor takes optional `privatekeyhex` (defaults to TestKeys.KEY3_HEX)

**Tests:** bitcoin/tests/test_wallet.py (18 tests)

**Main usage:**
```python
from bitcoin.wallet import Wallet

# Create with default key (KEY3_HEX)
wallet = Wallet()

# Create from private key
wallet = Wallet(private_key_hex)

# Access keypair
pub = wallet.keypair.publickey
address = wallet.get_address()

# WIF conversion
wif = wallet.export_wif()
wallet = Wallet.from_wif(wif)

# Generate random wallet
wallet = Wallet.generate()

# Sign and verify
signature = wallet.sign_message(message_hash)
is_valid = wallet.verify_message(message_hash, signature)
```

**Uses:** KeyPair class from cryptography module

**Dependencies:** cryptography.keypair, config

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

#### transaction.py ✓ (NEW - OBJECT ORIENTED)
**Transaction class for creating and sending Bitcoin transactions**

Object-oriented transaction creation with wallet integration.

**Class: Transaction**
- Constructor takes `wallet` parameter
- `raw_txn` - Raw transaction hex (set after create())
- `signed` - Boolean flag for transaction state

**Tests:** bitcoin/tests/test_transaction.py (20 tests)

**Main usage:**
```python
from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction

# Create wallet and transaction
wallet = Wallet.from_wif(wif)
transaction = Transaction(wallet)

# Create signed transaction
signed_txn = transaction.create(
    prev_txn_hash="c39e394d...",
    prev_output_index=0,
    source_address="133txdx...",
    outputs=[
        [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
        [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
    ]
)

# Verify signature
is_valid = transaction.verify()

# Get transaction hash (TXID)
txid = transaction.get_transaction_hash()
# Use txid as prev_txn_hash in next transaction

# Send to network with chunk receiving (WARNING: broadcasts to mainnet!)
# transaction.send(receive_response=True)  # Receives and processes chunks
# transaction.send(receive_response=False) # Send only, no response
```

**Uses:** Wallet class, txnUtils, msgUtils

**Dependencies:** bitcoin.wallet, bitcoin.txnUtils, bitcoin.msgUtils

#### txnUtils.py ✓
**Transaction utilities (library - legacy)**

Core transaction functions:
- `makeRawTransaction()` - Build unsigned transaction
- `makeSignedTransaction()` - Create and sign with ECDSA
- `verifyTxnSignature()` - Verify signature is valid
- ScriptSig and ScriptPubKey generation

**Note:** For new code, prefer using Transaction class for better OOP design.

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
| wallet.py | 18 ✓ | Production | **OOP Wallet class** |
| transaction.py | 20 ✓ | Production | **OOP Transaction class** |
| msgUtils.py | 2 ✓ | Production | Protocol & P2P messages |
| txnUtils.py | 5 ✓ | Production | Transaction utils (legacy) |
| myWallet.py | - | Working | Wallet functions (legacy) |
| makeAddr.py | - | Working | Address generator |
| myTransaction.py | - | Working | Multi-method test |
| minimalPeerConnection.py | - | Working | Network demo |
| minimalSendTxn.py | - | Working | TX broadcast |
| sendBitcoinTransaction.py | - | Working | Advanced P2P |
| mine.py | - | Working | Mining demo |
| txnUtilsMod.py | - | Archive | Modified version |

**Total:** 45 tests passing (18 wallet + 20 transaction + 2 msgUtils + 5 txnUtils)

## Testing

Run all tests:
```bash
cd bitcoin/tests

python test_wallet.py       # 18 tests - OOP Wallet class
python test_transaction.py  # 20 tests - OOP Transaction class (includes hash tests)
python test_msgUtils.py     # 2 tests - Protocol & P2P messages
python test_txnUtils.py     # 5 tests - Transaction utils (legacy)
```

**Note:** Cryptography tests are in `cryptography/tests/`

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

## Advanced Concepts

### Transaction Fees

Bitcoin transaction fees are calculated based on transaction size in bytes, not the amount transferred.

**Fee calculation:**
```
Fee = Transaction Size (bytes) × Fee Rate (satoshis/byte)
```

**Transaction size estimation:**
- Basic transaction (1 input, 2 outputs): ~250 bytes
- Each additional input: ~148 bytes
- Each additional output: ~34 bytes

**Example:**
```
Transaction with 1 input, 2 outputs:
Size: 250 bytes
Fee rate: 10 sat/byte
Total fee: 2,500 satoshis (0.000025 BTC)
```

**Setting fee rate:**
- Check mempool congestion
- Use fee estimation APIs
- Typical range: 1-100 sat/byte depending on network conditions
- Higher fees = faster confirmation

**Implementation:**
```python
# Calculate transaction size (estimate)
inputs = 1
outputs = 2
estimated_size = 250 + (inputs - 1) * 148 + (outputs - 2) * 34

# Set fee rate (satoshis per byte)
fee_rate = 10  # sat/byte

# Calculate total fee
fee = estimated_size * fee_rate

# Subtract fee from output amount
output_amount = input_amount - fee
```

**Important:** The fee is not explicitly listed in the transaction. It's the difference between input and output amounts:
```
Fee = Sum(inputs) - Sum(outputs)
```

### Testing Transactions

**Methods to test before broadcasting:**

1. **Testnet** - Separate Bitcoin network with free test coins
   - Different network magic: 0x0709110B
   - Different port: 18333
   - Test coins from faucets
   - Identical protocol, zero value

2. **Regtest** (Regression Test)
   - Local private blockchain
   - Generate blocks instantly
   - Complete control over network
   - Perfect for development

3. **Local Validation**
   - Build transaction locally
   - Verify signature without broadcasting
   - Use `verifyTxnSignature()` function
   - Check transaction structure

4. **Decode Raw Transaction**
   - Use Bitcoin Core's `decoderawtransaction`
   - Inspect all fields before sending
   - Verify addresses and amounts
   - Check script validity

**Example validation:**
```python
from bitcoin import txnUtils

# Create signed transaction
signed_txn = txnUtils.makeSignedTransaction(...)

# Verify signature locally (no broadcast)
is_valid = txnUtils.verifyTxnSignature(signed_txn)

if is_valid:
    print("Transaction is valid!")
    # Now safe to broadcast
else:
    print("Transaction signature invalid!")
```

### HD Wallets (BIP32/BIP39)

The current implementation uses single private keys (one key = one address). Production wallets use Hierarchical Deterministic (HD) wallets for better privacy and key management.

**BIP39: Mnemonic Seed Phrases**

Convert random entropy to memorable words:
```
Random Entropy (128-256 bits)
  ↓
Mnemonic Words (12-24 words)
  ↓ PBKDF2-HMAC-SHA512 (with optional passphrase)
Master Seed (512 bits)
```

**Example mnemonic (12 words):**
```
witch collapse practice feed shame open despair creek road again ice least
```

**BIP32: Hierarchical Deterministic Keys**

Derive unlimited keys from single master seed:
```
Master Seed (512 bits)
  ↓ Split
Master Private Key (256 bits) + Chain Code (256 bits)
  ↓ For each derivation
HMAC-SHA512(chain_code, parent_key + index)
  ↓ Split
Child Private Key + Child Chain Code
```

**Derivation Path Structure:**
```
m / purpose' / coin_type' / account' / change / address_index

Example: m/44'/0'/0'/0/0
- m: Master key
- 44': BIP44 (hardened derivation, indicated by ')
- 0': Bitcoin (coin type)
- 0': Account 0
- 0: External chain (receiving addresses)
- 0: First address

Next address: m/44'/0'/0'/0/1
Change address: m/44'/0'/0'/1/0
```

**Advantages of HD Wallets:**
- Single backup (mnemonic) for infinite addresses
- Better privacy (new address per transaction)
- Organized structure (accounts, change addresses)
- Can derive public keys without private keys (watch-only wallets)

**Implementation note:**
This educational codebase uses simple single-key wallets. For HD wallet implementation, see production libraries like `python-bitcoinlib` or `pycoin`.

**Derivation process:**
```python
# Pseudocode for key derivation
def derive_child_key(parent_key, chain_code, index):
    if index >= 0x80000000:  # Hardened derivation
        data = b'\x00' + parent_key + index.to_bytes(4, 'big')
    else:  # Normal derivation
        data = parent_public_key + index.to_bytes(4, 'big')

    # HMAC-SHA512
    I = hmac.new(chain_code, data, hashlib.sha512).digest()

    # Split result
    child_key = (int.from_bytes(I[:32]) + parent_key) % n
    child_chain_code = I[32:]

    return child_key, child_chain_code
```

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
