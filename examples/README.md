# Examples

Example scripts demonstrating how to use the bitcoin-code library.

## Running Examples

All examples should be run from the project root:

```bash
cd C:\Users\robbi\PycharmProjects\bitcoin-code
python examples/example_4bit.py
```

## Available Examples

### example_4bit.py
**4-bit ECDSA Rollback Examples**

Demonstrates how to use `RollbackECDSA4bit` to recover private keys:
- Public key rollback (brute force, BSGS, Pollard's Rho)
- Nonce recovery attack
- Comparing all attack methods
- Shor's quantum algorithm simulation

```bash
python examples/example_4bit.py
```

### example_4bit_detailed_backup.py
**Detailed 4-bit ECDSA Operations**

Step-by-step trace through ECDSA operations:
- Keypair generation with intermediate values
- Signature creation traced
- Signature verification traced
- Nonce reuse attack demonstration
- Complete point multiplication table

```bash
python examples/example_4bit_detailed_backup.py
```

### example_keypair.py
**KeyPair Class Usage**

Demonstrates the object-oriented `KeyPair` class:
- Creating keypairs from private keys
- Generating random keypairs
- WIF conversion
- Sign and verify messages

```bash
python examples/example_keypair.py
```

### generate_from_seed_phrase.py
**BIP39 Seed Phrase Wallet Generation**

Shows how to generate Bitcoin wallets from 12-word seed phrases:
- Using `bip39.mnemonic_to_wallet()`
- Using `KeyPair.from_mnemonic()`
- With optional passphrase
- Step-by-step conversion

```bash
python examples/generate_from_seed_phrase.py
```

### example_usage.py
**Rollback System Usage**

Examples of using the rollback system:
- Basic RIPEMD-160 rollback
- Quiet mode operation
- Diagnostic runner with configuration
- ECDSA rollback placeholder
- Backward compatibility with old interface

```bash
python examples/example_usage.py
```

## Notes

- All examples use `sys.path.insert` to find the parent modules
- Run from the project root directory for correct imports
- These are educational demonstrations, not production code
