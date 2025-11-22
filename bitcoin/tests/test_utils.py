"""
Test suite for Bitcoin utility functions

Tests utils.py which handles:
- Variable-length integer encoding (varint)
- Variable-length string encoding (varstr)
- Network address formatting
- Base58 encoding/decoding
- Base58Check encoding/decoding
- Base256 encoding/decoding
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from bitcoin import utils


class TestUtils(unittest.TestCase):
    """Test Bitcoin utility functions."""

    def test_varint(self):
        """Test variable-length integer encoding."""
        self.assertEqual(utils.varint(0x42), '\x42')
        self.assertEqual(utils.varint(0x123), '\xfd\x23\x01')
        self.assertEqual(utils.varint(0x12345678), '\xfe\x78\x56\x34\x12')

    def test_processVarInt(self):
        """Test variable-length integer decoding."""
        self.assertEqual(utils.processVarInt(utils.varint(0x42)), [0x42, 1])
        self.assertEqual(utils.processVarInt(utils.varint(0x1234)), [0x1234, 3])

    def test_varstr(self):
        """Test variable-length string encoding."""
        self.assertEqual(utils.varstr('abc'), '\x03abc')

    def test_processVarStr(self):
        """Test variable-length string decoding."""
        self.assertEqual(utils.processVarStr('\x03abc'), ['abc', 4])

    def test_processAddr(self):
        """Test network address parsing."""
        # Format: services(8) + IPv6-mapped IPv4(12) + IP(4) + port(2)
        addr_bytes = 'x' * 20 + '\x62\x91\x98\x16\x20\x8d'
        self.assertEqual(utils.processAddr(addr_bytes), '98.145.152.22:8333')

    def test_countLeadingCharacters(self):
        """Test counting leading characters."""
        self.assertEqual(utils.countLeadingChars('a\0bcd\0', '\0'), 0)
        self.assertEqual(utils.countLeadingChars('\0\0a\0bcd\0', '\0'), 2)
        self.assertEqual(utils.countLeadingChars('1a\0bcd\0', '1'), 1)

    def test_base256_encode(self):
        """Test base256 encoding."""
        self.assertEqual(utils.base256encode(0x4142), 'AB')

    def test_base256_decode(self):
        """Test base256 decoding."""
        self.assertEqual(utils.base256decode('AB'), 0x4142)

    def test_base256_roundtrip(self):
        """Test base256 encoding/decoding roundtrip."""
        self.assertEqual(utils.base256encode(utils.base256decode('abc')), 'abc')

    def test_base58_decode(self):
        """Test base58 decoding."""
        self.assertEqual(utils.base58decode('121'), 58)
        self.assertEqual(
            utils.base58decode('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'),
            0x800C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D507A5B8D
        )

    def test_base58_roundtrip(self):
        """Test base58 encoding/decoding roundtrip."""
        self.assertEqual(utils.base58encode(utils.base58decode('abc')), 'abc')

    def test_base58check_roundtrip(self):
        """Test base58check encoding/decoding roundtrip."""
        self.assertEqual(utils.base58CheckDecode(utils.base58CheckEncode(42, 'abc')), 'abc')
        self.assertEqual(utils.base58CheckDecode(utils.base58CheckEncode(0, '\0\0abc')), '\0\0abc')

    def test_base58check_wif(self):
        """Test base58check encoding for WIF (Wallet Import Format)."""
        # Test WIF encoding
        s = utils.base256encode(0x0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D)
        b = utils.base58CheckEncode(0x80, s)
        self.assertEqual(b, "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ")


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
