"""
Wallet class for Bitcoin key and transaction management

Provides a higher-level interface for Bitcoin operations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.keypair import KeyPair
from config import TestKeys


class Wallet:
    """
    Bitcoin wallet for managing keys and transactions.

    Attributes:
        keypair (KeyPair): The ECDSA key pair for this wallet
    """

    def __init__(self, privatekeyhex=None):
        """
        Initialize Wallet with a private key.

        Args:
            privatekeyhex (str, optional): Private key as hex string (64 characters).
                                          Defaults to TestKeys.KEY3_HEX if not provided.
        """
        if privatekeyhex is None:
            privatekeyhex = TestKeys.KEY3_HEX

        # Create keypair instance variable
        self.keypair = KeyPair(privatekeyhex)

    def get_address(self):
        """
        Get the Bitcoin address for this wallet.

        Returns:
            str: Bitcoin address (Base58Check encoded)
        """
        return self.keypair.get_address()

    def get_public_key(self):
        """
        Get the public key for this wallet.

        Returns:
            str: Hex-encoded public key
        """
        return self.keypair.publickey

    def get_private_key(self):
        """
        Get the private key for this wallet.

        Returns:
            str: Hex-encoded private key
        """
        return self.keypair.get_private_key()

    def export_wif(self, compressed=False):
        """
        Export private key in WIF format.

        Args:
            compressed (bool): Whether to use compressed WIF format

        Returns:
            str: WIF-encoded private key
        """
        return self.keypair.to_wif(compressed)

    def sign_message(self, message_hash):
        """
        Sign a message hash.

        Args:
            message_hash (bytes): Hash to sign (typically SHA-256)

        Returns:
            bytes: DER-encoded signature
        """
        return self.keypair.sign(message_hash)

    def verify_message(self, message_hash, signature):
        """
        Verify a signature.

        Args:
            message_hash (bytes): Hash that was signed
            signature (bytes): DER-encoded signature

        Returns:
            bool: True if signature is valid
        """
        return self.keypair.verify(message_hash, signature)

    @classmethod
    def from_wif(cls, wif):
        """
        Create Wallet from WIF-encoded private key.

        Args:
            wif (str): WIF-encoded private key

        Returns:
            Wallet: New Wallet instance
        """
        keypair = KeyPair.from_wif(wif)
        # Create wallet with the private key
        wallet = cls(keypair.get_private_key())
        return wallet

    @classmethod
    def generate(cls):
        """
        Generate a new random Wallet.

        Returns:
            Wallet: New Wallet with random private key
        """
        keypair = KeyPair.generate()
        return cls(keypair.get_private_key())

    def __repr__(self):
        """String representation (doesn't expose private key)."""
        return f"Wallet(address='{self.get_address()}')"

    def __str__(self):
        """User-friendly string representation."""
        return f"Bitcoin Wallet\nAddress: {self.get_address()}\nPublic Key: {self.keypair.publickey[:20]}..."
