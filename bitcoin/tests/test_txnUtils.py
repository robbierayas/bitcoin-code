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
from config import TestKeys, TestTransactions, TestRawTransactions


class TestTxnUtils(unittest.TestCase):
    """Test Bitcoin transaction utility functions."""

    def test_parseTxn(self):
        """Test parsing a Bitcoin transaction."""
        parsed = txnUtils.parseTxn(TestTransactions.TXN_SIGNED)

        # Check parsed components
        self.assertEqual(parsed[0], "0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000")
        self.assertEqual(parsed[1], TestTransactions.TXN_SIG_DER[:-2] + "01")
        self.assertEqual(parsed[2], TestTransactions.TXN_PUBKEY)
        self.assertEqual(parsed[3], "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                                   "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

    def test_getSignableTxn(self):
        """Test generating signable version of transaction."""
        parsed = txnUtils.parseTxn(TestTransactions.TXN_SIGNED)
        signableTxn = txnUtils.getSignableTxn(parsed)
        self.assertEqual(signableTxn, TestTransactions.TXN_SIGNABLE)

    def test_verifyTxnSignature(self):
        """Test verifying a transaction signature."""
        # Should verify without raising assertion error
        txnUtils.verifyTxnSignature(TestTransactions.TXN_SIGNED)

    def test_makeRawTransaction(self):
        """Test creating raw transaction."""
        # http://bitcoin.stackexchange.com/questions/3374/how-to-redeem-a-basic-tx
        txn = txnUtils.makeRawTransaction(
            TestRawTransactions.RAW_TX_PREV_HASH,
            TestRawTransactions.RAW_TX_SOURCE_INDEX,
            TestRawTransactions.RAW_TX_SCRIPT_SIG,
            [[TestRawTransactions.RAW_TX_SATOSHIS,
              TestRawTransactions.RAW_TX_OUTPUT_SCRIPT]],
        ) + "01000000"  # hash code type

        self.assertEqual(txn, TestRawTransactions.RAW_TX_EXPECTED)

    def test_makeSignedTransaction(self):
        """Test creating and signing a complete transaction."""
        # Transaction from
        # https://blockchain.info/tx/901a53e7a3ca96ed0b733c0233aad15f11b0c9e436294aa30c367bf06c3b7be8
        # From 133t to 1KKKK
        privateKey = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)

        outputs = [[amount, keyUtils.addrHashToScriptPubKey(addr)]
                   for amount, addr in TestTransactions.BLOCKCHAIN_TX_OUTPUTS]

        signed_txn = txnUtils.makeSignedTransaction(
            privateKey,
            TestTransactions.BLOCKCHAIN_TX_HASH,
            TestTransactions.BLOCKCHAIN_TX_SOURCE_INDEX,
            keyUtils.addrHashToScriptPubKey(TestKeys.TXN_TEST_ADDR),
            outputs
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
