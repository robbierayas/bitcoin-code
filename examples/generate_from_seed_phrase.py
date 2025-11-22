#!/usr/bin/env python
"""
Example: Generate Bitcoin wallet from BIP39 seed phrase

This script demonstrates how to generate a Bitcoin wallet from a 12-word
BIP39 mnemonic seed phrase.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography import bip39
from cryptography.keypair import KeyPair


def main():
    # Example seed phrase (user-provided test phrase)
    mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"

    print("="*70)
    print("Bitcoin Wallet Generation from BIP39 Seed Phrase")
    print("="*70)
    print()

    # Method 1: Using the bip39 module directly
    print("Method 1: Using bip39.mnemonic_to_wallet()")
    print("-" * 70)
    wallet = bip39.mnemonic_to_wallet(mnemonic)
    print(f"Mnemonic:     {mnemonic}")
    print(f"Private Key:  {wallet['private_key']}")
    print(f"WIF:          {wallet['wif']}")
    print(f"Address:      {wallet['address']}")
    print(f"Public Key:   {wallet['public_key'][:40]}...")
    print(f"Chain Code:   {wallet['chain_code']}")
    print()

    # Method 2: Using KeyPair.from_mnemonic()
    print("Method 2: Using KeyPair.from_mnemonic()")
    print("-" * 70)
    keypair = KeyPair.from_mnemonic(mnemonic)
    print(f"Mnemonic:     {mnemonic}")
    print(f"Private Key:  {keypair.get_private_key()}")
    print(f"WIF:          {keypair.to_wif()}")
    print(f"Address:      {keypair.get_address()}")
    print(f"Public Key:   {keypair.publickey[:40]}...")
    print()

    # Method 3: With optional passphrase for additional security
    print("Method 3: With optional passphrase")
    print("-" * 70)
    passphrase = "my_secret_passphrase"
    keypair_with_pass = KeyPair.from_mnemonic(mnemonic, passphrase)
    print(f"Mnemonic:     {mnemonic}")
    print(f"Passphrase:   {passphrase}")
    print(f"Private Key:  {keypair_with_pass.get_private_key()}")
    print(f"WIF:          {keypair_with_pass.to_wif()}")
    print(f"Address:      {keypair_with_pass.get_address()}")
    print(f"Public Key:   {keypair_with_pass.publickey[:40]}...")
    print()

    # Method 4: Step-by-step conversion
    print("Method 4: Step-by-step conversion")
    print("-" * 70)
    print("Step 1: Mnemonic -> Seed (PBKDF2)")
    seed = bip39.mnemonic_to_seed(mnemonic)
    print(f"  Seed (64 bytes): {seed.hex()[:60]}...")
    print()

    print("Step 2: Seed -> Master Key (BIP32)")
    private_key, chain_code = bip39.seed_to_master_key(seed)
    print(f"  Private Key: {private_key}")
    print(f"  Chain Code:  {chain_code}")
    print()

    print("Step 3: Private Key -> KeyPair")
    keypair = KeyPair(private_key)
    print(f"  Address: {keypair.get_address()}")
    print()

    print("="*70)
    print("All methods produce the same deterministic wallet!")
    print("="*70)


if __name__ == '__main__':
    main()
