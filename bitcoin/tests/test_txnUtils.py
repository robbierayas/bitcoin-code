"""
Test suite for Bitcoin transaction utilities

Tests txnUtils.py which handles:
- Raw transaction creation
- Transaction parsing
- Transaction signing and verification
- ScriptSig and ScriptPubKey generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from cryptography import keyUtils
from bitcoin import txnUtils


class TestTxnUtils(unittest.TestCase):
    """Test Bitcoin transaction utility functions."""

    def test_parseTxn(self):
        """Test parsing a Bitcoin transaction."""
        txn = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
               "8a47" +
               "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
               "41" +
               "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
               "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
               "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        parsed = txnUtils.parseTxn(txn)

        # Check parsed components
        self.assertEqual(parsed[0], "0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000")
        self.assertEqual(parsed[1], "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01")
        self.assertEqual(parsed[2], "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55")
        self.assertEqual(parsed[3], "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                                   "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

    def test_getSignableTxn(self):
        """Test generating signable version of transaction."""
        txn = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
               "8a47" +
               "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
               "41" +
               "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
               "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
               "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        parsed = txnUtils.parseTxn(txn)
        myTxn_forSig = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "1976a914" + "167c74f7491fe552ce9e1912810a984355b8ee07" + "88ac" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000" +
                        "01000000")

        signableTxn = txnUtils.getSignableTxn(parsed)
        self.assertEqual(signableTxn, myTxn_forSig)

    def test_verifyTxnSignature(self):
        """Test verifying a transaction signature."""
        txn = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
               "8a47" +
               "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
               "41" +
               "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
               "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
               "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        # Should verify without raising assertion error
        txnUtils.verifyTxnSignature(txn)

    def test_makeRawTransaction(self):
        """Test creating raw transaction."""
        # http://bitcoin.stackexchange.com/questions/3374/how-to-redeem-a-basic-tx
        txn = txnUtils.makeRawTransaction(
            "f2b3eb2deb76566e7324307cd47c35eeb88413f971d88519859b1834307ecfec",  # output transaction hash
            1,  # sourceIndex
            "76a914010966776006953d5567439e5e39f86a0d273bee88ac",  # scriptSig
            [[99900000,  # satoshis
              "76a914097072524438d003d23a2f23edb65aae1bb3e46988ac"]],  # outputScript
        ) + "01000000"  # hash code type

        expected = ("0100000001eccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f2" +
                    "010000001976a914010966776006953d5567439e5e39f86a0d273bee88acffffffff" +
                    "01605af405000000001976a914097072524438d003d23a2f23edb65aae1bb3e46988ac" +
                    "0000000001000000")

        self.assertEqual(txn, expected)

    def test_makeSignedTransaction(self):
        """Test creating and signing a complete transaction."""
        # Transaction from
        # https://blockchain.info/tx/901a53e7a3ca96ed0b733c0233aad15f11b0c9e436294aa30c367bf06c3b7be8
        # From 133t to 1KKKK
        privateKey = keyUtils.wifToPrivateKey("5Kb6aGpijtrb8X28GzmWtbcGZCG8jHQWFJcWugqo3MwKRvC8zyu")  # 133t

        signed_txn = txnUtils.makeSignedTransaction(
            privateKey,
            "c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",  # output (prev) transaction hash
            0,  # sourceIndex
            keyUtils.addrHashToScriptPubKey("133txdxQmwECTmXqAr9RWNHnzQ175jGb7e"),
            [[24321,  # satoshis
              keyUtils.addrHashToScriptPubKey("1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa")],
             [20000,
              keyUtils.addrHashToScriptPubKey("15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7")]]
        )

        # Should create valid signed transaction (verified internally by makeSignedTransaction)
        self.assertIsNotNone(signed_txn)
        self.assertGreater(len(signed_txn), 0)

        # Verify the signature
        txnUtils.verifyTxnSignature(signed_txn)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTxnUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
