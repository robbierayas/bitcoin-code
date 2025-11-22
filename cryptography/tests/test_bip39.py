"""
Test suite for BIP39 mnemonic implementation

Tests bip39.py which handles:
- Mnemonic to seed conversion (PBKDF2)
- Seed to master key derivation (BIP32)
- Mnemonic to private key
- Mnemonic to wallet generation
- KeyPair.from_mnemonic() class method
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from cryptography import bip39
from cryptography.keypair import KeyPair


class TestBIP39(unittest.TestCase):
    """Test BIP39 mnemonic seed phrase functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # User-provided test mnemonic
        self.test_mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"

        # Standard BIP39 test vector from the specification
        # https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki#test-vectors
        # Note: Official test vectors use "TREZOR" as passphrase
        self.bip39_test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        self.bip39_test_passphrase = "TREZOR"
        self.bip39_test_seed = "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
        # BIP32 master key derived from the seed (using HMAC-SHA512 with "Bitcoin seed")
        self.bip39_test_private_key = "cbedc75b0d6412c85c79bc13875112ef912fd1e756631b5a00330866f22ff184"
        self.bip39_test_chain_code = "a3fa8c983223306de0f0f65e74ebb1e98aba751633bf91d5fb56529aa5c132c1"

    def test_mnemonic_to_seed_length(self):
        """Test that mnemonic_to_seed produces 64-byte seed."""
        seed = bip39.mnemonic_to_seed(self.test_mnemonic)
        self.assertEqual(len(seed), 64)
        self.assertIsInstance(seed, bytes)

    def test_mnemonic_to_seed_deterministic(self):
        """Test that same mnemonic always produces same seed."""
        seed1 = bip39.mnemonic_to_seed(self.test_mnemonic)
        seed2 = bip39.mnemonic_to_seed(self.test_mnemonic)
        self.assertEqual(seed1, seed2)

    def test_mnemonic_to_seed_with_passphrase(self):
        """Test that passphrase changes the seed."""
        seed_no_pass = bip39.mnemonic_to_seed(self.test_mnemonic, "")
        seed_with_pass = bip39.mnemonic_to_seed(self.test_mnemonic, "mypassphrase")
        self.assertNotEqual(seed_no_pass, seed_with_pass)

    def test_mnemonic_normalization(self):
        """Test that extra whitespace is normalized."""
        seed1 = bip39.mnemonic_to_seed("  grit   problem  ball  ")
        seed2 = bip39.mnemonic_to_seed("grit problem ball")
        self.assertEqual(seed1, seed2)

    def test_bip39_test_vector(self):
        """Test against official BIP39 test vector."""
        seed = bip39.mnemonic_to_seed(self.bip39_test_mnemonic, self.bip39_test_passphrase)
        self.assertEqual(seed.hex(), self.bip39_test_seed)

    def test_seed_to_master_key_length(self):
        """Test that seed_to_master_key produces correct key lengths."""
        seed = bip39.mnemonic_to_seed(self.test_mnemonic)
        private_key, chain_code = bip39.seed_to_master_key(seed)

        # Both should be 32 bytes (64 hex characters)
        self.assertEqual(len(private_key), 64)
        self.assertEqual(len(chain_code), 64)
        self.assertIsInstance(private_key, str)
        self.assertIsInstance(chain_code, str)

    def test_seed_to_master_key_deterministic(self):
        """Test that same seed produces same master key."""
        seed = bip39.mnemonic_to_seed(self.test_mnemonic)
        key1, chain1 = bip39.seed_to_master_key(seed)
        key2, chain2 = bip39.seed_to_master_key(seed)
        self.assertEqual(key1, key2)
        self.assertEqual(chain1, chain2)

    def test_bip39_test_vector_private_key(self):
        """Test master private key derivation against BIP39 test vector."""
        seed = bip39.mnemonic_to_seed(self.bip39_test_mnemonic, self.bip39_test_passphrase)
        private_key, chain_code = bip39.seed_to_master_key(seed)
        self.assertEqual(private_key, self.bip39_test_private_key)
        self.assertEqual(chain_code, self.bip39_test_chain_code)

    def test_mnemonic_to_private_key(self):
        """Test direct mnemonic to private key conversion."""
        private_key = bip39.mnemonic_to_private_key(self.test_mnemonic)

        # Should be 32 bytes (64 hex characters)
        self.assertEqual(len(private_key), 64)
        self.assertIsInstance(private_key, str)

        # Should be valid hex
        int(private_key, 16)

    def test_mnemonic_to_private_key_deterministic(self):
        """Test that same mnemonic produces same private key."""
        key1 = bip39.mnemonic_to_private_key(self.test_mnemonic)
        key2 = bip39.mnemonic_to_private_key(self.test_mnemonic)
        self.assertEqual(key1, key2)

    def test_mnemonic_to_wallet(self):
        """Test full wallet generation from mnemonic."""
        wallet = bip39.mnemonic_to_wallet(self.test_mnemonic)

        # Check all expected keys are present
        self.assertIn('private_key', wallet)
        self.assertIn('wif', wallet)
        self.assertIn('address', wallet)
        self.assertIn('public_key', wallet)
        self.assertIn('chain_code', wallet)

        # Validate formats
        self.assertEqual(len(wallet['private_key']), 64)  # 32 bytes hex
        self.assertEqual(len(wallet['chain_code']), 64)    # 32 bytes hex
        self.assertTrue(wallet['wif'].startswith('5'))     # Uncompressed WIF starts with 5
        self.assertTrue(wallet['address'].startswith('1')) # P2PKH address starts with 1
        self.assertTrue(wallet['public_key'].startswith('04'))  # Uncompressed pubkey

    def test_mnemonic_to_wallet_deterministic(self):
        """Test that same mnemonic produces same wallet."""
        wallet1 = bip39.mnemonic_to_wallet(self.test_mnemonic)
        wallet2 = bip39.mnemonic_to_wallet(self.test_mnemonic)

        self.assertEqual(wallet1['private_key'], wallet2['private_key'])
        self.assertEqual(wallet1['address'], wallet2['address'])
        self.assertEqual(wallet1['wif'], wallet2['wif'])

    def test_keypair_from_mnemonic(self):
        """Test KeyPair.from_mnemonic() class method."""
        keypair = KeyPair.from_mnemonic(self.test_mnemonic)

        self.assertIsInstance(keypair, KeyPair)
        self.assertTrue(keypair.get_address().startswith('1'))
        self.assertEqual(len(keypair.get_private_key()), 64)

    def test_keypair_from_mnemonic_deterministic(self):
        """Test that KeyPair.from_mnemonic() is deterministic."""
        keypair1 = KeyPair.from_mnemonic(self.test_mnemonic)
        keypair2 = KeyPair.from_mnemonic(self.test_mnemonic)

        self.assertEqual(keypair1.get_private_key(), keypair2.get_private_key())
        self.assertEqual(keypair1.get_address(), keypair2.get_address())
        self.assertEqual(keypair1.publickey, keypair2.publickey)

    def test_keypair_from_mnemonic_with_passphrase(self):
        """Test that KeyPair.from_mnemonic() respects passphrase."""
        keypair1 = KeyPair.from_mnemonic(self.test_mnemonic, "")
        keypair2 = KeyPair.from_mnemonic(self.test_mnemonic, "password123")

        self.assertNotEqual(keypair1.get_private_key(), keypair2.get_private_key())
        self.assertNotEqual(keypair1.get_address(), keypair2.get_address())

    def test_user_test_mnemonic(self):
        """
        Test the specific user-provided mnemonic.

        Mnemonic: "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
        """
        wallet = bip39.mnemonic_to_wallet(self.test_mnemonic)

        print("\n" + "="*70)
        print("User Test Mnemonic Results:")
        print("="*70)
        print(f"Mnemonic: {self.test_mnemonic}")
        print(f"Private Key: {wallet['private_key']}")
        print(f"WIF: {wallet['wif']}")
        print(f"Address: {wallet['address']}")
        print(f"Public Key: {wallet['public_key'][:40]}...")
        print(f"Chain Code: {wallet['chain_code']}")
        print("="*70)

        # Basic validation
        self.assertEqual(len(wallet['private_key']), 64)
        self.assertTrue(wallet['address'].startswith('1'))


class TestBIP39EdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_mnemonic(self):
        """Test handling of empty mnemonic."""
        # Should still work - PBKDF2 can handle empty password
        seed = bip39.mnemonic_to_seed("")
        self.assertEqual(len(seed), 64)

    def test_single_word_mnemonic(self):
        """Test handling of single word mnemonic."""
        seed = bip39.mnemonic_to_seed("word")
        self.assertEqual(len(seed), 64)

    def test_unicode_passphrase(self):
        """Test handling of unicode characters in passphrase."""
        mnemonic = "test test test"
        seed1 = bip39.mnemonic_to_seed(mnemonic, "café")
        seed2 = bip39.mnemonic_to_seed(mnemonic, "cafe")
        self.assertNotEqual(seed1, seed2)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestBIP39))
    suite.addTests(loader.loadTestsFromTestCase(TestBIP39EdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
