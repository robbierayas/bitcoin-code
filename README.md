# Bitcoin Protocol - Educational Implementation

Educational Python demonstrating Bitcoin at a low level.

**WARNING:** Educational use only. DO NOT use for real Bitcoin.

## Setup

**Windows:**
```bash
windowsSetup.bat
```

**Linux/Mac:**
```bash
pip install ecdsa pycryptodome
```

## How to Run

### Cryptography

**Test all modules:**
```bash
cd cryptography/tests
python test_base58Utils.py      # 11 tests - Base58 encoding
python test_keypair.py          # 24 tests - OOP KeyPair class
python test_keyUtils.py         # 9 tests - Legacy key functions
python test_ripemd160.py        # 15 tests - RIPEMD-160
```

**Using KeyPair (Object-Oriented):**
```python
from cryptography.keypair import KeyPair

# Create keypair
keypair = KeyPair(private_key_hex)

# Access public key (public attribute)
print(keypair.publickey)

# Get address
address = keypair.get_address()
```

**Files:**
- `cryptography/keypair.py` - OOP KeyPair class ✓
- `cryptography/keyUtils.py` - Legacy functions (uses KeyPair internally)
- `cryptography/ripemd160.py` - Production RIPEMD-160
- `cryptography/ripemd160_educational.py` - Educational version

### Bitcoin

**Using Wallet (Object-Oriented):**
```python
from bitcoin.wallet import Wallet

# Create wallet with default key
wallet = Wallet()

# Get address
address = wallet.get_address()

# Sign message
signature = wallet.sign_message(message_hash)
```

**Generate address:**
```bash
cd bitcoin
python makeAddr.py
```

**Create transaction:**
```bash
cd bitcoin
python makeTransaction.py
```

**Test multiple implementations:**
```bash
cd bitcoin
python myTransaction.py
```

**Network connection:**
```bash
cd bitcoin
python minimalPeerConnection.py
```

**Mining demo:**
```bash
cd bitcoin
python mine.py
```

**Run tests:**
```bash
cd bitcoin/tests
python test_wallet.py        # 18 tests - OOP Wallet
python test_msgUtils.py      # 2 tests
python test_txnUtils.py      # 5 tests
python test_myWallet.py      # 4 tests
```

### Rollback (Experimental)

**Run:**
```bash
cd bitcoin
python myTransaction.py
```

**File:** `cryptography/rollback.py`

---

## Configuration

Test keys and data are stored in `config.py`:
- Private keys for tests
- Sample transactions
- Test addresses and signatures

Import in tests:
```python
from config import TestKeys, TestTransactions, TestSignatures
```

## Documentation

- `bitcoin/README.md` - Bitcoin concepts and module details
- `cryptography/README.md` - RIPEMD-160 implementation details
- `CLAUDE.md` - Complete technical reference
- `config.py` - Test keys and configuration

## Resources

- [Bitcoins the hard way](http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html)
- [Bitcoin Protocol Spec](https://en.bitcoin.it/wiki/Protocol_documentation)
- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)
