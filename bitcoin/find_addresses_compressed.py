"""
Find addresses using Electrum's compressed public key format
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import hashlib
import unicodedata
from cryptography import bip32, base58Utils
from config import TestHDWallet


def normalize_electrum(text):
    text = unicodedata.normalize('NFKD', text)
    return ' '.join(text.split())


def electrum_mnemonic_to_seed(mnemonic, passphrase=''):
    mnemonic = normalize_electrum(mnemonic)
    passphrase = normalize_electrum(passphrase) if passphrase else ''
    salt = b'electrum' + passphrase.encode('utf-8')
    return hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt, 2048)


def get_compressed_address(node):
    """Get address using COMPRESSED public key (Electrum format)"""
    keypair = node.get_keypair()
    pubkey_hex = keypair.publickey

    # Convert uncompressed to compressed
    x = int(pubkey_hex[2:66], 16)
    y = int(pubkey_hex[66:], 16)
    compressed = bytes.fromhex(('02' if y % 2 == 0 else '03') + pubkey_hex[2:66])

    # Generate address from compressed public key
    sha256_hash = hashlib.sha256(compressed).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # Base58Check encode
    return base58Utils.base58CheckEncode(0x00, ripemd160_hash)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--max-index', type=int, default=2000, help='Max index to search')
    parser.add_argument('--show-first', type=int, default=10, help='Show first N addresses')
    args = parser.parse_args()

    targets = ['1DqEczkgKeQNDHCoMFubQebMEoNW3Bx7X5', '1EGHUD4NTGWR5n1bL9qroHqbTaMoPZE6a7']

    mnemonic = TestHDWallet.MNEMONIC_12
    seed = electrum_mnemonic_to_seed(mnemonic, '')
    master = bip32.master_key_from_seed(seed)

    print('Searching m/0/x with COMPRESSED public keys (Electrum format)...')
    print('=' * 80)

    found_count = 0
    for i in range(args.max_index):
        node = bip32.derive_from_path(master, f'm/0/{i}')
        addr = get_compressed_address(node)

        if addr in targets:
            print(f'\n[FOUND] {addr}')
            print(f'  Path: m/0/{i}')
            print(f'  Private key: {node.get_private_key_hex()}')
            found_count += 1
            if found_count == len(targets):
                print(f'\n[SUCCESS] Found all {len(targets)} target addresses!')
                break
        elif i < args.show_first:
            print(f'm/0/{i:4d}: {addr}')
        elif i % 100 == 0:
            print(f'Checked up to m/0/{i}...')

    if found_count < len(targets):
        print(f'\nFound {found_count} of {len(targets)} target addresses in first {args.max_index} indices')
        print('Try increasing --max-index or check if seed/passphrase is correct')
