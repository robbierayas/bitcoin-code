"""
Example usage of KeyPair class

Demonstrates object-oriented Bitcoin key management.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.keypair import KeyPair


def main():
    print("=" * 70)
    print("KeyPair Class Example - Object-Oriented Bitcoin Key Management")
    print("=" * 70)
    print()

    # Example 1: Create from existing private key
    print("1. Create KeyPair from private key:")
    print("-" * 70)
    private_key = "0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D"
    keypair = KeyPair(private_key)

    print(f"Private Key: {keypair.get_private_key()}")
    print(f"Public Key:  {keypair.publickey[:40]}...")
    print(f"Address:     {keypair.get_address()}")
    print()

    # Example 2: Generate random keypair
    print("2. Generate random KeyPair:")
    print("-" * 70)
    random_keypair = KeyPair.generate()
    print(f"Address:     {random_keypair.get_address()}")
    print(f"Public Key:  {random_keypair.publickey[:40]}...")
    print()

    # Example 3: WIF conversion
    print("3. WIF (Wallet Import Format) conversion:")
    print("-" * 70)
    wif = keypair.to_wif()
    print(f"WIF:         {wif}")

    # Restore from WIF
    restored = KeyPair.from_wif(wif)
    print(f"Restored:    {restored.get_address()}")
    print(f"Match:       {keypair.get_address() == restored.get_address()}")
    print()

    # Example 4: Sign and verify
    print("4. Sign and verify message:")
    print("-" * 70)
    import hashlib

    message = b"Hello, Bitcoin!"
    message_hash = hashlib.sha256(message).digest()

    signature = keypair.sign(message_hash)
    print(f"Message:     {message.decode()}")
    print(f"Signature:   {signature.hex()[:40]}...")

    is_valid = keypair.verify(message_hash, signature)
    print(f"Valid:       {is_valid}")
    print()

    # Example 5: Object representation
    print("5. Object representation:")
    print("-" * 70)
    print(f"repr():      {repr(keypair)}")
    print(f"str():       {str(keypair)}")
    print()

    print("=" * 70)
    print("KeyPair Benefits:")
    print("- Encapsulation: Private key is protected with _privatekey")
    print("- Public access: publickey is a public attribute")
    print("- Clean API: Methods like get_address(), to_wif(), sign()")
    print("- Type safety: Validation in constructor")
    print("=" * 70)


if __name__ == '__main__':
    main()
