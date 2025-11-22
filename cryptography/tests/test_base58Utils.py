"""
Test suite for Base58 encoding utilities.

Tests base58Utils.py which handles:
- Base58 encoding/decoding
- Base256 encoding/decoding
- Base58Check encoding/decoding with checksums
- Leading character counting
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from cryptography import base58Utils


class TestBase58Utils(unittest.TestCase):
    """Test Base58 and Base256 encoding functions."""

    def test_countLeadingCharacters(self):
        """Test counting leading characters in strings."""
        self.assertEqual(base58Utils.countLeadingChars(b'a\0bcd\0', 0), 0)
        self.assertEqual(base58Utils.countLeadingChars(b'\0\0a\0bcd\0', 0), 2)
        self.assertEqual(base58Utils.countLeadingChars('1a\0bcd\0', '1'), 1)

    def test_base256_roundtrip(self):
        """Test base256 encoding/decoding round trip."""
        original = b'abc'
        encoded = base58Utils.base256encode(base58Utils.base256decode(original))
        self.assertEqual(encoded, original)

    def test_base256_encode(self):
        """Test base256 encoding specific values."""
        self.assertEqual(base58Utils.base256encode(0x4142), b'AB')

    def test_base256_decode(self):
        """Test base256 decoding specific values."""
        self.assertEqual(base58Utils.base256decode(b'AB'), 0x4142)

    def test_base58_roundtrip(self):
        """Test base58 encoding/decoding round trip."""
        original = 'abc'
        encoded = base58Utils.base58encode(base58Utils.base58decode(original))
        self.assertEqual(encoded, original)

    def test_base58_decode_small(self):
        """Test base58 decoding small value."""
        self.assertEqual(base58Utils.base58decode('121'), 58)

    def test_base58_decode_wif(self):
        """Test base58 decoding WIF-encoded private key."""
        wif = '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
        expected = 0x800C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D507A5B8D
        self.assertEqual(base58Utils.base58decode(wif), expected)

    def test_base58check_roundtrip_simple(self):
        """Test Base58Check encoding/decoding with simple payload."""
        original = b'abc'
        encoded = base58Utils.base58CheckEncode(42, original)
        decoded = base58Utils.base58CheckDecode(encoded)
        self.assertEqual(decoded, original)

    def test_base58check_roundtrip_leading_zeros(self):
        """Test Base58Check with leading zero bytes."""
        original = b'\0\0abc'
        encoded = base58Utils.base58CheckEncode(0, original)
        decoded = base58Utils.base58CheckDecode(encoded)
        self.assertEqual(decoded, original)

    def test_base58check_wif_encoding(self):
        """Test Base58Check encoding produces correct WIF."""
        # Private key value
        key_int = 0x0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D
        s = base58Utils.base256encode(key_int)
        # WIF uses version 0x80
        wif = base58Utils.base58CheckEncode(0x80, s)
        self.assertEqual(wif, "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ")


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBase58Utils)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
