"""
Test suite for KeyPair class

Tests the object-oriented KeyPair implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import hashlib
import ecdsa

from cryptography.keypair import KeyPair
from config import TestKeys


class TestKeyPairBasics(unittest.TestCase):
    """Test basic KeyPair functionality."""

    def test_create_keypair_from_hex(self):
        """Test creating KeyPair from hex private key."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Should have public key
        self.assertIsNotNone(keypair.publickey)
        self.assertTrue(keypair.publickey.startswith('04'))
        self.assertEqual(len(keypair.publickey), 130)  # 65 bytes * 2

    def test_get_private_key(self):
        """Test getting private key."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Should return private key
        self.assertEqual(keypair.get_private_key(), TestKeys.KEY1_HEX)

    def test_private_key_is_private(self):
        """Test that private key is a private attribute."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Should not have direct access to _privatekey in public API
        # (it's still accessible in Python but discouraged)
        self.assertTrue(hasattr(keypair, '_privatekey'))

    def test_publickey_is_public(self):
        """Test that publickey is a public attribute."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Should have direct access to publickey
        self.assertIsNotNone(keypair.publickey)
        # Should be same as generated
        self.assertTrue(len(keypair.publickey) > 0)

    def test_invalid_private_key_length(self):
        """Test that invalid private key length raises error."""
        with self.assertRaises(ValueError):
            KeyPair("abc")  # Too short

    def test_invalid_private_key_hex(self):
        """Test that non-hex private key raises error."""
        with self.assertRaises(ValueError):
            KeyPair("z" * 64)  # Invalid hex


class TestKeyPairWIF(unittest.TestCase):
    """Test WIF conversion."""

    def test_to_wif(self):
        """Test converting to WIF."""
        keypair = KeyPair(TestKeys.KEY1_HEX)
        wif = keypair.to_wif()

        self.assertEqual(wif, TestKeys.KEY1_WIF)

    def test_from_wif(self):
        """Test creating from WIF."""
        keypair = KeyPair.from_wif(TestKeys.KEY1_WIF)

        self.assertEqual(keypair.get_private_key(), TestKeys.KEY1_HEX)

    def test_wif_roundtrip(self):
        """Test WIF roundtrip conversion."""
        original = KeyPair(TestKeys.KEY2_HEX)
        wif = original.to_wif()
        restored = KeyPair.from_wif(wif)

        self.assertEqual(original.get_private_key(), restored.get_private_key())
        self.assertEqual(original.publickey, restored.publickey)


class TestKeyPairAddress(unittest.TestCase):
    """Test Bitcoin address generation."""

    def test_get_address(self):
        """Test generating Bitcoin address."""
        keypair = KeyPair(TestKeys.KEY2_HEX)
        address = keypair.get_address()

        self.assertEqual(address, TestKeys.KEY2_ADDR)

    def test_address_format(self):
        """Test that address has correct format."""
        keypair = KeyPair(TestKeys.KEY1_HEX)
        address = keypair.get_address()

        # Bitcoin addresses start with 1 (mainnet P2PKH)
        self.assertTrue(address.startswith('1'))
        # Should be 34 characters
        self.assertEqual(len(address), 34)

    def test_different_keys_different_addresses(self):
        """Test that different keys produce different addresses."""
        keypair1 = KeyPair(TestKeys.KEY1_HEX)
        keypair2 = KeyPair(TestKeys.KEY2_HEX)

        self.assertNotEqual(keypair1.get_address(), keypair2.get_address())


class TestKeyPairGenerate(unittest.TestCase):
    """Test random key generation."""

    def test_generate_random_keypair(self):
        """Test generating random KeyPair."""
        keypair = KeyPair.generate()

        # Should have valid keys
        self.assertIsNotNone(keypair.publickey)
        self.assertIsNotNone(keypair.get_private_key())

        # Should be able to get address
        address = keypair.get_address()
        self.assertTrue(address.startswith('1'))

    def test_generate_creates_different_keys(self):
        """Test that generate creates different keys each time."""
        keypair1 = KeyPair.generate()
        keypair2 = KeyPair.generate()

        self.assertNotEqual(keypair1.get_private_key(), keypair2.get_private_key())
        self.assertNotEqual(keypair1.publickey, keypair2.publickey)


class TestKeyPairSigning(unittest.TestCase):
    """Test signing and verification."""

    def test_sign_message(self):
        """Test signing a message."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Create message hash
        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()

        # Sign
        signature = keypair.sign(message_hash)

        # Should produce signature
        self.assertIsNotNone(signature)
        self.assertTrue(len(signature) > 0)

    def test_verify_signature(self):
        """Test verifying a signature."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Create and sign message
        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()
        signature = keypair.sign(message_hash)

        # Verify
        is_valid = keypair.verify(message_hash, signature)
        self.assertTrue(is_valid)

    def test_verify_invalid_signature(self):
        """Test that invalid signature fails verification."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()

        # Create invalid signature
        invalid_signature = b'\x00' * 64

        # Should return False
        is_valid = keypair.verify(message_hash, invalid_signature)
        self.assertFalse(is_valid)

    def test_verify_wrong_message(self):
        """Test that signature doesn't verify for wrong message."""
        keypair = KeyPair(TestKeys.KEY1_HEX)

        # Sign one message
        message1 = b"Hello, Bitcoin!"
        message_hash1 = hashlib.sha256(message1).digest()
        signature = keypair.sign(message_hash1)

        # Try to verify with different message
        message2 = b"Different message"
        message_hash2 = hashlib.sha256(message2).digest()
        is_valid = keypair.verify(message_hash2, signature)

        self.assertFalse(is_valid)


class TestKeyPairDeterministic(unittest.TestCase):
    """Test deterministic behavior."""

    def test_same_private_key_same_public_key(self):
        """Test that same private key produces same public key."""
        keypair1 = KeyPair(TestKeys.KEY1_HEX)
        keypair2 = KeyPair(TestKeys.KEY1_HEX)

        self.assertEqual(keypair1.publickey, keypair2.publickey)

    def test_same_private_key_same_address(self):
        """Test that same private key produces same address."""
        keypair1 = KeyPair(TestKeys.KEY2_HEX)
        keypair2 = KeyPair(TestKeys.KEY2_HEX)

        self.assertEqual(keypair1.get_address(), keypair2.get_address())


class TestKeyPairStringRepresentation(unittest.TestCase):
    """Test string representations."""

    def test_repr(self):
        """Test __repr__ method."""
        keypair = KeyPair(TestKeys.KEY2_HEX)
        repr_str = repr(keypair)

        # Should contain address but not private key
        self.assertIn(TestKeys.KEY2_ADDR, repr_str)
        self.assertNotIn(TestKeys.KEY2_HEX, repr_str)

    def test_str(self):
        """Test __str__ method."""
        keypair = KeyPair(TestKeys.KEY2_HEX)
        str_repr = str(keypair)

        # Should contain address and partial public key
        self.assertIn(TestKeys.KEY2_ADDR, str_repr)
        self.assertIn('Bitcoin KeyPair', str_repr)
        # Should not expose full private key
        self.assertNotIn(TestKeys.KEY2_HEX, str_repr)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairWIF))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairAddress))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairGenerate))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairSigning))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairDeterministic))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyPairStringRepresentation))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
