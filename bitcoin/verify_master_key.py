"""
Verify that our master key derivation matches Electrum's

This script verifies:
1. Master xpub matches Electrum
2. Root fingerprint matches Electrum
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import hashlib
import unicodedata
from cryptography import bip32, base58Utils
from cryptography.keypair import KeyPair
from config import TestHDWallet


def normalize_electrum(text):
    """Normalize text exactly like Electrum does."""
    text = unicodedata.normalize('NFKD', text)
    text = ' '.join(text.split())
    return text


def electrum_mnemonic_to_seed(mnemonic, passphrase=''):
    """Convert Electrum mnemonic to seed using Electrum's method."""
    mnemonic = normalize_electrum(mnemonic)
    passphrase = normalize_electrum(passphrase) if passphrase else ''

    salt = b'electrum' + passphrase.encode('utf-8')
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt, 2048)
    return seed


def hash160(data):
    """HASH160 = RIPEMD160(SHA256(data))"""
    sha = hashlib.sha256(data).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    return ripe


def serialize_xpub(node):
    """
    Serialize BIP32Node to xpub format.

    xpub format (78 bytes):
    - 4 bytes: version (0x0488B21E for mainnet xpub)
    - 1 byte: depth
    - 4 bytes: parent fingerprint
    - 4 bytes: child number
    - 32 bytes: chain code
    - 33 bytes: public key (compressed)
    """
    # Version bytes for mainnet xpub
    version = bytes.fromhex('0488B21E')

    # Depth (master = 0)
    depth = node.depth.to_bytes(1, 'big')

    # Parent fingerprint (0x00000000 for master)
    parent_fp = node.fingerprint

    # Child number (0 for master)
    child_num = node.child_number.to_bytes(4, 'big')

    # Chain code
    chain_code = node.chain_code

    # Get compressed public key
    keypair = node.get_keypair()
    pubkey_hex = keypair.publickey
    # If uncompressed (starts with 04), convert to compressed
    if len(pubkey_hex) == 130:  # 65 bytes * 2 hex chars
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        x = pubkey_bytes[1:33]
        y = pubkey_bytes[33:65]
        # Compressed format: 02 or 03 prefix + x coordinate
        if int.from_bytes(y, 'big') % 2 == 0:
            compressed = b'\x02' + x
        else:
            compressed = b'\x03' + x
    else:
        compressed = bytes.fromhex(pubkey_hex)

    # Concatenate all parts
    xpub_bytes = version + depth + parent_fp + child_num + chain_code + compressed

    # Base58Check encode
    checksum = hashlib.sha256(hashlib.sha256(xpub_bytes).digest()).digest()[:4]
    xpub_with_checksum = xpub_bytes + checksum

    # Convert to base58
    xpub_int = int.from_bytes(xpub_with_checksum, 'big')
    xpub = base58Utils.base58encode(xpub_int)

    # Add leading '1's for leading zero bytes
    leading_zeros = len(xpub_with_checksum) - len(xpub_with_checksum.lstrip(b'\x00'))
    xpub = '1' * leading_zeros + xpub

    return xpub


def get_root_fingerprint(node):
    """
    Calculate BIP32 root fingerprint.

    Fingerprint = first 4 bytes of HASH160(compressed_pubkey)
    """
    keypair = node.get_keypair()
    pubkey_hex = keypair.publickey

    # Convert to compressed
    if len(pubkey_hex) == 130:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        x = pubkey_bytes[1:33]
        y = pubkey_bytes[33:65]
        if int.from_bytes(y, 'big') % 2 == 0:
            compressed = b'\x02' + x
        else:
            compressed = b'\x03' + x
    else:
        compressed = bytes.fromhex(pubkey_hex)

    # HASH160 and take first 4 bytes
    h160 = hash160(compressed)
    fingerprint = h160[:4].hex()

    return fingerprint


def verify_master_key(mnemonic, passphrase=''):
    """Verify master key matches Electrum."""
    print("=" * 80)
    print("MASTER KEY VERIFICATION")
    print("=" * 80)
    print()

    # Step 1: Derive master key
    print("Step 1: Deriving master key from mnemonic...")
    print(f"  Mnemonic: {mnemonic[:30]}...")
    print(f"  Passphrase: {'(empty)' if not passphrase else '(set)'}")

    seed = electrum_mnemonic_to_seed(mnemonic, passphrase)
    print(f"  PBKDF2 seed: {seed.hex()[:64]}...")

    master = bip32.master_key_from_seed(seed)
    print(f"  Master privkey: {master.private_key.hex()}")
    print(f"  Master chaincode: {master.chain_code.hex()}")
    print()

    # Step 2: Calculate xpub
    print("Step 2: Calculating master xpub...")
    xpub = serialize_xpub(master)
    print(f"  Calculated xpub: {xpub}")
    print(f"  Expected xpub:   {TestHDWallet.ELECTRUM_MASTER_XPUB}")

    if xpub == TestHDWallet.ELECTRUM_MASTER_XPUB:
        print("  [OK] XPUB MATCHES!")
    else:
        print("  [FAIL] XPUB MISMATCH!")
    print()

    # Step 3: Calculate fingerprint
    print("Step 3: Calculating root fingerprint...")
    fingerprint = get_root_fingerprint(master)
    print(f"  Calculated fingerprint: {fingerprint}")
    print(f"  Expected fingerprint:   {TestHDWallet.ELECTRUM_ROOT_FINGERPRINT}")

    if fingerprint == TestHDWallet.ELECTRUM_ROOT_FINGERPRINT:
        print("  [OK] FINGERPRINT MATCHES!")
    else:
        print("  [FAIL] FINGERPRINT MISMATCH!")
    print()

    # Summary
    print("=" * 80)
    if xpub == TestHDWallet.ELECTRUM_MASTER_XPUB and fingerprint == TestHDWallet.ELECTRUM_ROOT_FINGERPRINT:
        print("[SUCCESS] MASTER KEY VERIFIED - Derivation is correct!")
        print("  You can now safely use this to derive addresses.")
        return True
    else:
        print("[FAILED] MASTER KEY MISMATCH - Something is wrong with derivation")
        print("  Possible issues:")
        print("  - Wrong passphrase")
        print("  - Implementation error in seed derivation")
        print("  - Implementation error in xpub/fingerprint calculation")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--passphrase', default='', help='Seed extension passphrase')
    args = parser.parse_args()

    mnemonic = TestHDWallet.MNEMONIC_12
    success = verify_master_key(mnemonic, args.passphrase)

    sys.exit(0 if success else 1)
