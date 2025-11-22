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


class TestMyWallet(unittest.TestCase):
    """Test wallet creation and address generation."""

    def test_createAddress_returns_public_key(self):
        """Test that createAddress returns a valid public key."""
        private_key = 'a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f'
        public_key = myWallet.createAddress(private_key)

        # Should return hex string
        self.assertIsInstance(public_key, str)

        # Should start with 04 (uncompressed public key)
        self.assertTrue(public_key.startswith('04'))

        # Should be 130 characters (65 bytes * 2)
        self.assertEqual(len(public_key), 130)

    def test_createAddress_deterministic(self):
        """Test that same private key produces same public key."""
        private_key = '18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'

        public_key1 = myWallet.createAddress(private_key)
        public_key2 = myWallet.createAddress(private_key)
        public_key3 = myWallet.createAddress(private_key)

        self.assertEqual(public_key1, public_key2)
        self.assertEqual(public_key2, public_key3)

    def test_createAddress_produces_valid_address(self):
        """Test that public key can be converted to valid Bitcoin address."""
        # Known private key and expected address
        private_key = '18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'
        expected_address = '16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM'

        # Generate public key
        public_key = myWallet.createAddress(private_key)

        # Convert to address
        address = keyUtils.pubKeyToAddr(public_key)

        # Should match expected address
        self.assertEqual(address, expected_address)

    def test_different_private_keys_different_public_keys(self):
        """Test that different private keys produce different public keys."""
        private_key1 = '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D'
        private_key2 = '18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'

        public_key1 = myWallet.createAddress(private_key1)
        public_key2 = myWallet.createAddress(private_key2)

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
