"""
KeyPair class for Bitcoin ECDSA key management

Represents a Bitcoin key pair with public and private keys.
"""

import hashlib
import ecdsa
from cryptography import base58Utils


class KeyPair:
    """
    Bitcoin ECDSA key pair with public and private keys.

    Attributes:
        publickey (str): Hex-encoded public key (65 bytes uncompressed or 33 bytes compressed)
        _privatekey (str): Hex-encoded private key (32 bytes) - private attribute
    """

    def __init__(self, private_key_hex):
        """
        Initialize KeyPair from private key.

        Args:
            private_key_hex (str): Private key as hex string (64 characters)

        Raises:
            ValueError: If private key is invalid
        """
        if not isinstance(private_key_hex, str):
            raise ValueError("Private key must be a hex string")

        # Normalize to uppercase for consistency
        private_key_hex = private_key_hex.upper()

        if len(private_key_hex) != 64:
            raise ValueError("Private key must be 64 hex characters (32 bytes)")

        # Validate hex
        try:
            int(private_key_hex, 16)
        except ValueError:
            raise ValueError("Private key must be valid hexadecimal")

        # Store private key (private attribute)
        self._privatekey = private_key_hex

        # Generate and store public key (public attribute)
        self.publickey = self._generate_public_key()

    def _generate_public_key(self):
        """
        Generate public key from private key using ECDSA secp256k1.

        Returns:
            str: Hex-encoded uncompressed public key (130 characters)
        """
        # Create signing key from private key
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(self._privatekey),
            curve=ecdsa.SECP256k1
        )

        # Get verifying (public) key
        vk = sk.get_verifying_key()

        # Return uncompressed public key (04 + x + y)
        return '04' + vk.to_string().hex()

    def get_private_key(self):
        """
        Get private key (read-only access).

        Returns:
            str: Hex-encoded private key
        """
        return self._privatekey

    def to_wif(self, compressed=False):
        """
        Convert private key to Wallet Import Format (WIF).

        Args:
            compressed (bool): Whether to use compressed WIF format

        Returns:
            str: WIF-encoded private key
        """
        # Add version byte (0x80 for mainnet)
        extended = bytes([0x80]) + bytes.fromhex(self._privatekey)

        # Add compression flag if needed
        if compressed:
            extended += b'\x01'

        # Add checksum and encode
        return base58Utils.base58CheckEncode(0x80, bytes.fromhex(self._privatekey))

    def get_address(self):
        """
        Generate Bitcoin address from public key.

        Returns:
            str: Bitcoin address (Base58Check encoded)
        """
        # SHA-256 hash of public key
        sha256_hash = hashlib.sha256(bytes.fromhex(self.publickey)).digest()

        # RIPEMD-160 hash of SHA-256 hash
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()

        # Base58Check encode with version 0x00 (P2PKH)
        return base58Utils.base58CheckEncode(0x00, hash160)

    def sign(self, message_hash):
        """
        Sign a message hash with private key.

        Args:
            message_hash (bytes): Hash to sign (typically SHA-256)

        Returns:
            bytes: DER-encoded signature
        """
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(self._privatekey),
            curve=ecdsa.SECP256k1
        )
        return sk.sign_digest(message_hash, sigencode=ecdsa.util.sigencode_der)

    def verify(self, message_hash, signature):
        """
        Verify a signature using public key.

        Args:
            message_hash (bytes): Hash that was signed
            signature (bytes): DER-encoded signature

        Returns:
            bool: True if signature is valid
        """
        vk = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(self.publickey[2:]),  # Skip '04' prefix
            curve=ecdsa.SECP256k1
        )
        try:
            vk.verify_digest(signature, message_hash, sigdecode=ecdsa.util.sigdecode_der)
            return True
        except (ecdsa.BadSignatureError, Exception):
            return False

    @classmethod
    def from_wif(cls, wif):
        """
        Create KeyPair from WIF-encoded private key.

        Args:
            wif (str): WIF-encoded private key

        Returns:
            KeyPair: New KeyPair instance
        """
        # Decode WIF
        decoded = base58Utils.base58CheckDecode(wif)

        # Check if compressed (33 bytes vs 32 bytes)
        if len(decoded) == 33:
            # Remove compression flag
            private_key = decoded[:-1]
        else:
            private_key = decoded

        return cls(private_key.hex())

    @classmethod
    def generate(cls):
        """
        Generate a new random KeyPair.

        Returns:
            KeyPair: New KeyPair with random private key
        """
        # Generate random private key
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        private_key_hex = sk.to_string().hex()
        return cls(private_key_hex)

    def __repr__(self):
        """String representation (doesn't expose private key)."""
        return f"KeyPair(address='{self.get_address()}')"

    def __str__(self):
        """User-friendly string representation."""
        return f"Bitcoin KeyPair\nAddress: {self.get_address()}\nPublic Key: {self.publickey[:20]}..."
