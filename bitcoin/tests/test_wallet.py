"""
Test suite for Wallet class

Tests the object-oriented Wallet implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import hashlib

from bitcoin.wallet import Wallet
from config import TestKeys


class TestWalletBasics(unittest.TestCase):
    """Test basic Wallet functionality."""

    def test_create_wallet_with_key(self):
        """Test creating Wallet with private key."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        # Should have keypair attribute
        self.assertIsNotNone(wallet.keypair)
        self.assertIsNotNone(wallet.keypair.publickey)

    def test_create_wallet_default_key(self):
        """Test creating Wallet with default key (KEY3_HEX)."""
        wallet = Wallet()

        # Should use KEY3_HEX by default (uppercased)
        self.assertEqual(wallet.get_private_key(), TestKeys.KEY3_HEX.upper())

    def test_get_address(self):
        """Test getting Bitcoin address."""
        wallet = Wallet(TestKeys.KEY2_HEX)
        address = wallet.get_address()

        self.assertEqual(address, TestKeys.KEY2_ADDR)

    def test_get_public_key(self):
        """Test getting public key."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        pubkey = wallet.get_public_key()

        # Should be uncompressed public key
        self.assertTrue(pubkey.startswith('04'))
        self.assertEqual(len(pubkey), 130)

    def test_get_private_key(self):
        """Test getting private key."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        self.assertEqual(wallet.get_private_key(), TestKeys.KEY1_HEX)


class TestWalletWIF(unittest.TestCase):
    """Test WIF operations."""

    def test_export_wif(self):
        """Test exporting to WIF."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        wif = wallet.export_wif()

        self.assertEqual(wif, TestKeys.KEY1_WIF)

    def test_from_wif(self):
        """Test creating Wallet from WIF."""
        wallet = Wallet.from_wif(TestKeys.KEY1_WIF)

        self.assertEqual(wallet.get_private_key(), TestKeys.KEY1_HEX)
        # Should produce valid address
        address = wallet.get_address()
        self.assertTrue(address.startswith('1'))

    def test_wif_roundtrip(self):
        """Test WIF export and import roundtrip."""
        original = Wallet(TestKeys.KEY2_HEX)
        wif = original.export_wif()
        restored = Wallet.from_wif(wif)

        self.assertEqual(original.get_private_key(), restored.get_private_key())
        self.assertEqual(original.get_address(), restored.get_address())


class TestWalletGenerate(unittest.TestCase):
    """Test random wallet generation."""

    def test_generate_random_wallet(self):
        """Test generating random Wallet."""
        wallet = Wallet.generate()

        # Should have valid keys
        self.assertIsNotNone(wallet.keypair)
        self.assertIsNotNone(wallet.get_private_key())
        self.assertIsNotNone(wallet.get_public_key())

        # Should be able to get address
        address = wallet.get_address()
        self.assertTrue(address.startswith('1'))

    def test_generate_creates_different_wallets(self):
        """Test that generate creates different wallets each time."""
        wallet1 = Wallet.generate()
        wallet2 = Wallet.generate()

        self.assertNotEqual(wallet1.get_private_key(), wallet2.get_private_key())
        self.assertNotEqual(wallet1.get_address(), wallet2.get_address())


class TestWalletSigning(unittest.TestCase):
    """Test signing and verification."""

    def test_sign_message(self):
        """Test signing a message."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()

        signature = wallet.sign_message(message_hash)

        # Should produce signature
        self.assertIsNotNone(signature)
        self.assertTrue(len(signature) > 0)

    def test_verify_message(self):
        """Test verifying a signature."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        # Create and sign message
        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()
        signature = wallet.sign_message(message_hash)

        # Verify
        is_valid = wallet.verify_message(message_hash, signature)
        self.assertTrue(is_valid)

    def test_verify_invalid_signature(self):
        """Test that invalid signature fails verification."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        message = b"Hello, Bitcoin!"
        message_hash = hashlib.sha256(message).digest()

        # Create invalid signature
        invalid_signature = b'\x00' * 64

        # Should return False
        is_valid = wallet.verify_message(message_hash, invalid_signature)
        self.assertFalse(is_valid)

    def test_verify_wrong_message(self):
        """Test that signature doesn't verify for wrong message."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        # Sign one message
        message1 = b"Hello, Bitcoin!"
        message_hash1 = hashlib.sha256(message1).digest()
        signature = wallet.sign_message(message_hash1)

        # Try to verify with different message
        message2 = b"Different message"
        message_hash2 = hashlib.sha256(message2).digest()
        is_valid = wallet.verify_message(message_hash2, signature)

        self.assertFalse(is_valid)


class TestWalletDeterministic(unittest.TestCase):
    """Test deterministic behavior."""

    def test_same_key_same_address(self):
        """Test that same key produces same address."""
        wallet1 = Wallet(TestKeys.KEY1_HEX)
        wallet2 = Wallet(TestKeys.KEY1_HEX)

        self.assertEqual(wallet1.get_address(), wallet2.get_address())

    def test_different_keys_different_addresses(self):
        """Test that different keys produce different addresses."""
        wallet1 = Wallet(TestKeys.KEY1_HEX)
        wallet2 = Wallet(TestKeys.KEY2_HEX)

        self.assertNotEqual(wallet1.get_address(), wallet2.get_address())


class TestWalletStringRepresentation(unittest.TestCase):
    """Test string representations."""

    def test_repr(self):
        """Test __repr__ method."""
        wallet = Wallet(TestKeys.KEY2_HEX)
        repr_str = repr(wallet)

        # Should contain address but not private key
        self.assertIn(TestKeys.KEY2_ADDR, repr_str)
        self.assertNotIn(TestKeys.KEY2_HEX, repr_str)

    def test_str(self):
        """Test __str__ method."""
        wallet = Wallet(TestKeys.KEY2_HEX)
        str_repr = str(wallet)

        # Should contain address and partial public key
        self.assertIn(TestKeys.KEY2_ADDR, str_repr)
        self.assertIn('Bitcoin Wallet', str_repr)
        # Should not expose full private key
        self.assertNotIn(TestKeys.KEY2_HEX, str_repr)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWalletBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestWalletWIF))
    suite.addTests(loader.loadTestsFromTestCase(TestWalletGenerate))
    suite.addTests(loader.loadTestsFromTestCase(TestWalletSigning))
    suite.addTests(loader.loadTestsFromTestCase(TestWalletDeterministic))
    suite.addTests(loader.loadTestsFromTestCase(TestWalletStringRepresentation))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
