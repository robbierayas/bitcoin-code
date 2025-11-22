"""
Test suite for Bitcoin key utilities

Tests keyUtils.py which handles:
- Private key to WIF conversion
- Public key generation from private keys
- Address generation from keys
- DER signature encoding
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import hashlib
import ecdsa
import ecdsa.der

from cryptography import base58Utils, keyUtils
from config import TestKeys, TestSignatures, TestTransactions


class TestKeyUtils(unittest.TestCase):
    """Test Bitcoin key utility functions."""

    def test_privateKeyToWif(self):
        """Test converting private key to WIF format."""
        w = keyUtils.privateKeyToWif(TestKeys.KEY1_HEX)
        self.assertEqual(w, TestKeys.KEY1_WIF)

    def test_WifToPrivateKey(self):
        """Test converting WIF back to private key."""
        k = keyUtils.wifToPrivateKey(TestKeys.KEY1_WIF)
        self.assertEqual(k.upper(), TestKeys.KEY1_HEX)

    def test_keyToAddr(self):
        """Test generating Bitcoin address from private key."""
        a = keyUtils.keyToAddr(TestKeys.KEY2_HEX)
        self.assertEqual(a, TestKeys.KEY2_ADDR)

    def test_pairs1(self):
        """Test key/address pairs from blockchain.info and multibit."""
        # blockchain.info
        wallet_key = base58Utils.base256encode(base58Utils.base58decode(TestKeys.BLOCKCHAIN_INFO_PRIVATE))
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), TestKeys.BLOCKCHAIN_INFO_ADDR)

        # can import into multibit
        wallet_key = base58Utils.base58CheckDecode(TestKeys.MULTIBIT_WIF)
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), TestKeys.MULTIBIT_ADDR)

        self.assertEqual(keyUtils.keyToAddr(TestKeys.BLOCKCHAIN_INFO_KEY), TestKeys.BLOCKCHAIN_INFO_ADDR)

    def test_pairs2(self):
        """Test key/address pair from gobittest.appspot.com."""
        # http://gobittest.appspot.com/Address
        # Cannot import into multibit
        self.assertEqual(keyUtils.keyToAddr(TestKeys.GOBI_KEY), TestKeys.GOBI_ADDR)

    def test_pairs3(self):
        """Test key/address pair from bitaddress.org."""
        # Can import into multibit
        # http://bitaddress.org
        wallet_key = base58Utils.base58CheckDecode(TestKeys.BITADDRESS_WIF)
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), TestKeys.BITADDRESS_ADDR)

    def test_der(self):
        """Test DER encoding of integers."""
        self.assertEqual(ecdsa.der.encode_sequence(
            ecdsa.der.encode_integer(0x123456),
            ecdsa.der.encode_integer(0x89abcd)).hex(),
                         "300b020312345602040089abcd")

    def test_derSigToHexSig(self):
        """Test converting DER signature to hex signature format."""
        self.assertEqual(TestSignatures.HEX_SIG,
                         keyUtils.derSigToHexSig(TestSignatures.DER_SIG))

    def test_transaction_signature(self):
        """Test transaction signature verification."""
        hashToSign = hashlib.sha256(hashlib.sha256(bytes.fromhex(TestTransactions.TXN_SIGNABLE)).digest()).digest().hex()
        sig_der = TestTransactions.TXN_SIG_DER[:-2]
        sig = keyUtils.derSigToHexSig(sig_der)

        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(TestTransactions.TXN_PUBKEY[2:]), curve=ecdsa.SECP256k1)
        self.assertEqual(vk.verify_digest(bytes.fromhex(sig), bytes.fromhex(hashToSign)), True)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestKeyUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
