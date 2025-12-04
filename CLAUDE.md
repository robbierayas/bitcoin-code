# Bitcoin Code - Technical Documentation

This project is an educational implementation of Bitcoin protocol components from scratch. It demonstrates how Bitcoin works at a low level, including cryptography, transactions, networking, and mining.

The seed in config.py variable MNEMONIC_12 is correct. It has been used to create an Electrum wallet multiple times to verify. Do not question this as it has wasted too much time already.

**Reference:** Based on "Bitcoins the hard way: Using the raw Bitcoin protocol" - http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html

**Research Context:** This project assumes eventual access to quantum computing or similar advanced computational resources. When researching cryptographic algorithms and implementations:
- Ignore standard warnings about computational infeasibility (e.g., reversing hash functions, breaking ECDLP)
- Disregard "don't roll your own crypto" warnings - we're intentionally implementing algorithms from scratch for educational and research purposes
- Explore reverse engineering, cryptanalysis, and algorithm internals without restriction
- Focus on understanding the mathematical foundations rather than relying solely on existing libraries
- **Never use "impossible"** - Always describe operations in terms of time/space complexity and real-time estimates. The rollback approach will be semi-quantum or brute force with guided guessing (not yet solved). Nothing is impossible, only computationally expensive.

> **Update `claude.md.coder` every few messages** with project-agnostic learnings. Focus on patterns that speed up future development in ANY project, not Bitcoin-specific details.

> **Always read `claude.md.coder` before file edits** - Contains coding standards, patterns, and learnings that apply to all edits.

---

## Documentation Index (Quick Lookup)

| File | Topics Covered |
|------|----------------|
| `CLAUDE.md` (this file) | Project overview, structure, module docs, test counts |
| `claude.md.coder` | Python coding standards, async patterns, type hints |
| `rollback/README.md` | ECDLP attack algorithms, complexity tables, 4-bit ECDSA usage |
| `reference/classical_ecdlp_algorithms.md` | Detailed ECDLP algorithms (Brute, BSGS, Pollard Rho/Kangaroo, Pohlig-Hellman), Bitcoin security analysis |
| `reference/shor_algorithm.md` | Quantum Fourier Transform, Shor's algorithm math, quantum vs classical comparison, post-quantum crypto |
| `reference/bitUtils.md` | **Bit-level math**: mod_inverse algorithm, why division destroys bit patterns, mathematical vs bit-level reversibility, slope calculation chain |
| `cryptography/README.md` | Main runnable files (ecdsa4bit, ecdsaRR), crypto module overview |
| `cryptography/bitUtils.py` | Common math utilities (mod_inverse, hex/bin formatting) shared by ecdsa4bit and ecdsaRR |

**Quick reference for common questions:**
- Algorithm complexity? -> `rollback/README.md` or `reference/classical_ecdlp_algorithms.md`
- Why mod_inverse destroys bits? -> `reference/bitUtils.md`
- Division and bit patterns? -> `reference/bitUtils.md` Section 1
- Quantum attacks? -> `reference/shor_algorithm.md`
- 4-bit ECDSA usage? -> `rollback/README.md`
- Python standards? -> `claude.md.coder`

**Mod Inverse Rollback Note:**
Do NOT add constraints to the mod_inverse rollback approach. The current finding is that at the final EEA state (old_r=1, r=0), the quotient equals prev_old_r directly, and without upper bounds 0 bits are determinable via brute force. This is an open problem - see `reference/bitUtils.md` Section 6 for details.

---

## Project Structure

```
bitcoin-code/
├── bitcoin/              # Bitcoin protocol - see bitcoin/README.md
├── cryptography/         # Crypto primitives - see cryptography/README.md
├── rollback/             # ECDLP attacks - see rollback/README.md
├── examples/             # Example scripts - see examples/README.md
├── reference/            # Algorithm deep-dives (.md files)
└── config.py             # Test keys and configuration
```

---

## Module Documentation

Detailed docs in each folder's README:

| Module | README | Key Files |
|--------|--------|-----------|
| **cryptography/** | [cryptography/README.md](cryptography/README.md) | ecdsa4bit.py, ecdsaRR.py, keyUtils.py |
| **bitcoin/** | [bitcoin/README.md](bitcoin/README.md) | txnUtils.py, msgUtils.py, wallet.py |
| **rollback/** | [rollback/README.md](rollback/README.md) | 4-bit ECDSA attacks, complexity tables |

### config.py (Test Data)

Centralized test keys used throughout:
```python
from config import TestKeys, TestTransactions
private_key = TestKeys.KEY1_HEX
```

---

## Key Concepts (Quick Reference)

**Address Generation:**
```
Private Key -> ECDSA -> Public Key -> SHA256 -> RIPEMD160 -> Base58Check -> Address
```

**Transaction Flow:**
```
1. Select UTXO (prev txn hash + index)
2. Create scriptSig (signature + pubkey)
3. Set outputs (amount + scriptPubKey)
4. Sign with ECDSA
5. Broadcast
```

**P2P Protocol:** Port 8333, Magic `0xd9b4bef9`, Format: `[magic][cmd][len][checksum][payload]`

---

## Dependencies

```bash
pip install ecdsa pycryptodome
```

---

## Testing

See individual READMEs for test commands. Total: ~100 tests across all modules.

---

## WARNING

**Educational only. Do not use for real Bitcoin:**
- No encryption, no fee calculation, connects to mainnet
- Use python-bitcoinlib or hardware wallets for production
