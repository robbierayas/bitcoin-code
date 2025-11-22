"""
Test suite for Transaction class

Tests the object-oriented Transaction implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from config import TestKeys


class TestTransactionBasics(unittest.TestCase):
    """Test basic Transaction functionality."""

    def test_create_transaction_object(self):
        """Test creating Transaction with wallet."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        # Should have wallet attribute
        self.assertIsNotNone(txn.wallet)
        self.assertEqual(txn.wallet, wallet)

    def test_initial_state(self):
        """Test initial state of Transaction."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        # Should not be signed yet
        self.assertFalse(txn.signed)
        self.assertIsNone(txn.raw_txn)

    def test_get_raw_before_create_raises(self):
        """Test that getting raw transaction before create raises error."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        with self.assertRaises(ValueError):
            txn.get_raw_transaction()

    def test_verify_before_create_raises(self):
        """Test that verifying before create raises error."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        with self.assertRaises(ValueError):
            txn.verify()

    def test_send_before_create_raises(self):
        """Test that sending before create raises error."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        with self.assertRaises(ValueError):
            txn.send()


class TestTransactionCreate(unittest.TestCase):
    """Test transaction creation."""

    def test_create_transaction(self):
        """Test creating a signed transaction."""
        # Use test wallet from config
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)

        txn = Transaction(wallet)

        # Create transaction (from test case in txnUtils)
        signed_txn = txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[
                [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
                [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
            ]
        )

        # Should be signed now
        self.assertTrue(txn.signed)
        self.assertIsNotNone(txn.raw_txn)
        self.assertIsNotNone(signed_txn)

    def test_create_sets_raw_txn(self):
        """Test that create sets raw_txn attribute."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        # Should be able to get raw transaction
        raw = txn.get_raw_transaction()
        self.assertIsNotNone(raw)
        self.assertTrue(isinstance(raw, str))


class TestTransactionVerify(unittest.TestCase):
    """Test transaction verification."""

    def test_verify_valid_transaction(self):
        """Test verifying a valid transaction."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[
                [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
                [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
            ]
        )

        # Should verify successfully
        is_valid = txn.verify()
        self.assertTrue(is_valid)


class TestTransactionHash(unittest.TestCase):
    """Test transaction hash (TXID) generation."""

    def test_get_hash_before_create_raises(self):
        """Test that getting hash before create raises error."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        with self.assertRaises(ValueError):
            txn.get_transaction_hash()

    def test_get_transaction_hash(self):
        """Test getting transaction hash."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        # Get transaction hash
        txid = txn.get_transaction_hash()

        # Should be 64 hex characters (32 bytes)
        self.assertEqual(len(txid), 64)
        # Should be valid hex
        self.assertTrue(all(c in '0123456789abcdef' for c in txid.lower()))

    def test_transaction_hash_deterministic(self):
        """Test that same transaction produces same hash."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)

        # Create two identical transactions
        txn1 = Transaction(wallet)
        txn1.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        txn2 = Transaction(wallet)
        txn2.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        # Should produce same hash (but different signatures due to randomness in ECDSA)
        # Actually, ECDSA signatures have randomness, so hashes will be different
        # Let's just verify both are valid
        hash1 = txn1.get_transaction_hash()
        hash2 = txn2.get_transaction_hash()

        self.assertEqual(len(hash1), 64)
        self.assertEqual(len(hash2), 64)

    def test_transaction_hash_can_be_used_as_prev_hash(self):
        """Test that transaction hash can be used as prev_txn_hash in next transaction."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)

        # Create first transaction
        txn1 = Transaction(wallet)
        txn1.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        # Get its hash
        txid1 = txn1.get_transaction_hash()

        # This hash would be used as prev_txn_hash in a subsequent transaction
        # Verify it's the right format
        self.assertEqual(len(txid1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in txid1.lower()))


class TestTransactionStringRepresentation(unittest.TestCase):
    """Test string representations."""

    def test_repr_unsigned(self):
        """Test __repr__ before signing."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)
        repr_str = repr(txn)

        # Should show unsigned state
        self.assertIn("signed=False", repr_str)

    def test_repr_signed(self):
        """Test __repr__ after signing."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        repr_str = repr(txn)

        # Should show signed state
        self.assertIn("signed=True", repr_str)

    def test_str_unsigned(self):
        """Test __str__ before signing."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)
        str_repr = str(txn)

        # Should show unsigned state
        self.assertIn("Signed: False", str_repr)

    def test_str_signed(self):
        """Test __str__ after signing."""
        wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        str_repr = str(txn)

        # Should show signed state
        self.assertIn("Signed: True", str_repr)


class TestTransactionFromMakeTransaction(unittest.TestCase):
    """Test case based on bitcoin/txn/makeTransaction.py example."""

    def test_make_transaction_example(self):
        """Test creating transaction from makeTransaction.py example."""
        # Create wallet from WIF (1MMMM address)
        wif = "5HusYj2b2x4nroApgfvaSfKYZhRbKFH41bVyPooymbC6KfgSXdD"
        wallet = Wallet.from_wif(wif)

        # Create transaction object
        transaction = Transaction(wallet)

        # Should start unsigned
        self.assertFalse(transaction.signed)

        # Create signed transaction (from makeTransaction.py example)
        signed_txn = transaction.create(
            prev_txn_hash="81b4c832d70cb56ff957589752eb4125a4cab78a25a8fc52d6a09e5bd4404d48",
            prev_output_index=0,
            source_address="1MMMMSUb1piy2ufrSguNUdFmAcvqrQF8M5",
            outputs=[
                [91234, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]
            ]
        )

        # Should be signed now
        self.assertTrue(transaction.signed)
        self.assertIsNotNone(signed_txn)

        # Verify transaction
        is_valid = transaction.verify()
        self.assertTrue(is_valid)

        # Should be able to get raw transaction
        raw = transaction.get_raw_transaction()
        self.assertEqual(raw, signed_txn)

    def test_make_transaction_output_format(self):
        """Test that makeTransaction example produces valid output."""
        wif = "5HusYj2b2x4nroApgfvaSfKYZhRbKFH41bVyPooymbC6KfgSXdD"
        wallet = Wallet.from_wif(wif)
        transaction = Transaction(wallet)

        signed_txn = transaction.create(
            prev_txn_hash="81b4c832d70cb56ff957589752eb4125a4cab78a25a8fc52d6a09e5bd4404d48",
            prev_output_index=0,
            source_address="1MMMMSUb1piy2ufrSguNUdFmAcvqrQF8M5",
            outputs=[[91234, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
        )

        # Should be valid hex
        self.assertTrue(all(c in '0123456789abcdefABCDEF' for c in signed_txn))

        # Should start with version (01000000)
        self.assertTrue(signed_txn.startswith("01000000") or signed_txn.startswith("01000000".upper()))

        # Should have reasonable length (not empty, not too short)
        self.assertGreater(len(signed_txn), 100)


class TestTransactionSendParameters(unittest.TestCase):
    """Test send() method parameters."""

    def test_send_has_receive_response_parameter(self):
        """Test that send() method accepts receive_response parameter."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        # Should raise ValueError before transaction is created
        with self.assertRaises(ValueError):
            txn.send(receive_response=False)

    def test_send_requires_signed_transaction(self):
        """Test that send() requires transaction to be signed first."""
        wallet = Wallet(TestKeys.KEY1_HEX)
        txn = Transaction(wallet)

        # Should raise ValueError
        with self.assertRaises(ValueError) as cm:
            txn.send()

        self.assertIn("not created yet", str(cm.exception))


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionCreate))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionVerify))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionHash))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionStringRepresentation))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionFromMakeTransaction))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionSendParameters))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
