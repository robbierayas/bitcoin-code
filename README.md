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

### Cryptography (RIPEMD-160)

**Test:**
```bash
cd cryptography/tests
python test_ripemd160.py                   # Production (15 tests)
python test_ripemd160_educational.py       # Educational (13 tests)
```

**Files:**
- `cryptography/ripemd160.py` - Production version
- `cryptography/ripemd160_educational.py` - Debug output version

### Bitcoin

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

## Documentation

- `bitcoin/README.md` - Bitcoin concepts and module details
- `cryptography/README.md` - RIPEMD-160 implementation details
- `CLAUDE.md` - Complete technical reference

## Resources

- [Bitcoins the hard way](http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html)
- [Bitcoin Protocol Spec](https://en.bitcoin.it/wiki/Protocol_documentation)
- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)
