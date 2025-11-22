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


class TestKeyUtils(unittest.TestCase):
    """Test Bitcoin key utility functions."""

    def test_privateKeyToWif(self):
        """Test converting private key to WIF format."""
        w = keyUtils.privateKeyToWif("0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D")
        self.assertEqual(w, "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ")

    def test_WifToPrivateKey(self):
        """Test converting WIF back to private key."""
        k = keyUtils.wifToPrivateKey("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ")
        self.assertEqual(k.upper(), "0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D")

    def test_keyToAddr(self):
        """Test generating Bitcoin address from private key."""
        a = keyUtils.keyToAddr("18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725")
        self.assertEqual(a, "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM")

    def test_pairs1(self):
        """Test key/address pairs from blockchain.info and multibit."""
        # blockchain.info
        wallet_addr = "1EyBEhrriJeghX4iqATQEWDq38Ae8ubBJe"
        wallet_private = "8tnArBrrp4KHVjv8WA6HiX4ev56WDhqGA16XJCHJzhNH"
        wallet_key = base58Utils.base256encode(base58Utils.base58decode(wallet_private))
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), wallet_addr)

        # can import into multibit
        bitcoin_qt = "5Jhw8B9J9QLaMmcBRfz7x8KkD9gwbNoyBMfWyANqiDwm3FFwgGC"
        wallet_key = base58Utils.base58CheckDecode(bitcoin_qt)
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), wallet_addr)

        wallet_key = "754580de93eea21579441b58e0c9b09f54f6005fc71135f5cfac027394b22caa"
        self.assertEqual(keyUtils.keyToAddr(wallet_key), wallet_addr)

    def test_pairs2(self):
        """Test key/address pair from gobittest.appspot.com."""
        # http://gobittest.appspot.com/Address
        # Cannot import into multibit
        wallet_private = "BB08A897EA1E422F989D36DE8D8186D8406BE25E577FD2A66976BF172325CDC9"
        wallet_addr = "1MZ1nxFpvUgaPYYWaLPkLGAtKjRqcCwbGh"
        self.assertEqual(keyUtils.keyToAddr(wallet_private), wallet_addr)

    def test_pairs3(self):
        """Test key/address pair from bitaddress.org."""
        # Can import into multibit
        # http://bitaddress.org
        wallet_private = "5J8PhneLEaL9qEPvW5voRgrELeXcmM12B6FbiA9wZAwDMnJMb2L"
        wallet_addr = "1Q2SuNLDXDtda7DPnBTocQWtUg1v4xZMrV"
        wallet_key = base58Utils.base58CheckDecode(wallet_private)
        self.assertEqual(keyUtils.keyToAddr(wallet_key.hex()), wallet_addr)

    def test_der(self):
        """Test DER encoding of integers."""
        self.assertEqual(ecdsa.der.encode_sequence(
            ecdsa.der.encode_integer(0x123456),
            ecdsa.der.encode_integer(0x89abcd)).hex(),
                         "300b020312345602040089abcd")

    def test_derSigToHexSig(self):
        """Test converting DER signature to hex signature format."""
        derSig = "304502204c01fee2d724fb2e34930c658f585d49be2f6ac87c126506c0179e6977716093022100faad0afd3ae536cfe11f83afaba9a8914fc0e70d4c6d1495333b2fb3df6e8cae"
        self.assertEqual("4c01fee2d724fb2e34930c658f585d49be2f6ac87c126506c0179e6977716093faad0afd3ae536cfe11f83afaba9a8914fc0e70d4c6d1495333b2fb3df6e8cae",
                         keyUtils.derSigToHexSig(derSig))

    def test_transaction_signature(self):
        """Test transaction signature verification."""
        txn = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
               "8a47" +
               "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
               "41" +
               "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
               "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
               "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        myTxn_forSig = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "1976a914" + "167c74f7491fe552ce9e1912810a984355b8ee07" + "88ac" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000" +
                        "01000000")

        public_key = "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55"
        hashToSign = hashlib.sha256(hashlib.sha256(bytes.fromhex(myTxn_forSig)).digest()).digest().hex()
        sig_der = "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01"[:-2]
        sig = keyUtils.derSigToHexSig(sig_der)

        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key[2:]), curve=ecdsa.SECP256k1)
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
