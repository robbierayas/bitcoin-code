"""
Example usage of Wallet class

Demonstrates object-oriented Bitcoin wallet management.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bitcoin.wallet import Wallet
from config import TestKeys


def main():
    print("=" * 70)
    print("Wallet Class Example - Object-Oriented Bitcoin Wallet Management")
    print("=" * 70)
    print()

    # Example 1: Create wallet with default key (KEY3_HEX)
    print("1. Create Wallet with default key:")
    print("-" * 70)
    wallet = Wallet()
    print(f"Address:     {wallet.get_address()}")
    print(f"Public Key:  {wallet.get_public_key()[:40]}...")
    print(f"Private Key: {wallet.get_private_key()[:20]}...{wallet.get_private_key()[-20:]}")
    print()

    # Example 2: Create wallet from existing private key
    print("2. Create Wallet from private key:")
    print("-" * 70)
    wallet2 = Wallet(TestKeys.KEY1_HEX)
    print(f"Address:     {wallet2.get_address()}")
    print(f"Public Key:  {wallet2.get_public_key()[:40]}...")
    print()

    # Example 3: Generate random wallet
    print("3. Generate random Wallet:")
    print("-" * 70)
    random_wallet = Wallet.generate()
    print(f"Address:     {random_wallet.get_address()}")
    print(f"Public Key:  {random_wallet.get_public_key()[:40]}...")
    print()

    # Example 4: WIF export and import
    print("4. WIF (Wallet Import Format) conversion:")
    print("-" * 70)
    wif = wallet2.export_wif()
    print(f"WIF:         {wif}")

    # Restore from WIF
    restored = Wallet.from_wif(wif)
    print(f"Restored:    {restored.get_address()}")
    print(f"Match:       {wallet2.get_address() == restored.get_address()}")
    print()

    # Example 5: Sign and verify
    print("5. Sign and verify message:")
    print("-" * 70)
    import hashlib

    message = b"Hello, Bitcoin!"
    message_hash = hashlib.sha256(message).digest()

    signature = wallet2.sign_message(message_hash)
    print(f"Message:     {message.decode()}")
    print(f"Signature:   {signature.hex()[:40]}...")

    is_valid = wallet2.verify_message(message_hash, signature)
    print(f"Valid:       {is_valid}")
    print()

    # Example 6: Object representation
    print("6. Object representation:")
    print("-" * 70)
    print(f"repr():      {repr(wallet2)}")
    print(f"str():       {str(wallet2)}")
    print()

    # Example 7: Accessing the keypair
    print("7. Accessing the KeyPair object:")
    print("-" * 70)
    print(f"Type:        {type(wallet.keypair)}")
    print(f"Publickey:   {wallet.keypair.publickey[:40]}...")
    print("Note: The keypair attribute gives direct access to KeyPair methods")
    print()

    print("=" * 70)
    print("Wallet Benefits:")
    print("- High-level API: Simple methods for common operations")
    print("- Default key: Uses KEY3_HEX if no key provided")
    print("- Encapsulation: Wraps KeyPair for wallet-specific operations")
    print("- Clean interface: get_address(), export_wif(), sign_message()")
    print("- Factory methods: from_wif(), generate()")
    print("=" * 70)


if __name__ == '__main__':
    main()
