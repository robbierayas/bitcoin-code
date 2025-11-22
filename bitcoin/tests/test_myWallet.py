"""
Test suite for Bitcoin wallet utilities

Tests myWallet.py which handles:
- Creating public keys from private keys
- Wallet address generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from bitcoin import myWallet
from bitcoin import keyUtils
from config import TestKeys


class TestMyWallet(unittest.TestCase):
    """Test wallet creation and address generation."""

    def test_createAddress_returns_public_key(self):
        """Test that createAddress returns a valid public key."""
        public_key = myWallet.createAddress(TestKeys.KEY3_HEX)

        # Should return hex string
        self.assertIsInstance(public_key, str)

        # Should start with 04 (uncompressed public key)
        self.assertTrue(public_key.startswith('04'))

        # Should be 130 characters (65 bytes * 2)
        self.assertEqual(len(public_key), 130)

    def test_createAddress_deterministic(self):
        """Test that same private key produces same public key."""
        public_key1 = myWallet.createAddress(TestKeys.KEY2_HEX)
        public_key2 = myWallet.createAddress(TestKeys.KEY2_HEX)
        public_key3 = myWallet.createAddress(TestKeys.KEY2_HEX)

        self.assertEqual(public_key1, public_key2)
        self.assertEqual(public_key2, public_key3)

    def test_createAddress_produces_valid_address(self):
        """Test that public key can be converted to valid Bitcoin address."""
        # Generate public key
        public_key = myWallet.createAddress(TestKeys.KEY2_HEX)

        # Convert to address
        address = keyUtils.pubKeyToAddr(public_key)

        # Should match expected address
        self.assertEqual(address, TestKeys.KEY2_ADDR)

    def test_different_private_keys_different_public_keys(self):
        """Test that different private keys produce different public keys."""
        public_key1 = myWallet.createAddress(TestKeys.KEY1_HEX)
        public_key2 = myWallet.createAddress(TestKeys.KEY2_HEX)

        self.assertNotEqual(public_key1, public_key2)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMyWallet)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
