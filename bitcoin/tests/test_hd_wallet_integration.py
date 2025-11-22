"""
Test HD Wallet Integration

Tests the complete HD wallet functionality including:
- BIP32 key derivation
- Mnemonic seed phrases
- Wallet with HD support
- Transaction fee calculation
- Change address generation
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from cryptography import bip32
from cryptography import keyUtils
from config import TestHDWallet as HDWalletConfig, TestKeys, TestTransactions


class TestBIP32KeyDerivation(unittest.TestCase):
    """Test BIP32 key derivation functions."""

    def test_mnemonic_to_seed(self):
        """Test mnemonic to seed conversion."""
        mnemonic = HDWalletConfig.MNEMONIC_12
        seed = bip32.mnemonic_to_seed(mnemonic)

        # Check seed length
        self.assertEqual(len(seed), 64, "Seed should be 64 bytes")

        # Check deterministic (same mnemonic = same seed)
        seed2 = bip32.mnemonic_to_seed(mnemonic)
        self.assertEqual(seed, seed2, "Same mnemonic should produce same seed")

    def test_master_key_derivation(self):
        """Test master key derivation from seed."""
        seed = bip32.mnemonic_to_seed(HDWalletConfig.MNEMONIC_12)
        master = bip32.master_key_from_seed(seed)

        # Check master key attributes
        self.assertIsNotNone(master.private_key)
        self.assertEqual(len(master.private_key), 32)
        self.assertEqual(master.depth, 0)

    def test_child_key_derivation(self):
        """Test child key derivation."""
        seed = bip32.mnemonic_to_seed(HDWalletConfig.MNEMONIC_12)
        master = bip32.master_key_from_seed(seed)

        # Derive first child (hardened)
        child = bip32.derive_child_key(master, 0x80000000)

        self.assertEqual(child.depth, 1)
        self.assertTrue(child.is_hardened)
        self.assertNotEqual(child.private_key, master.private_key)

    def test_derivation_path(self):
        """Test full derivation path."""
        seed = bip32.mnemonic_to_seed(HDWalletConfig.MNEMONIC_12)
        master = bip32.master_key_from_seed(seed)

        # Derive m/44'/0'/0'/0/0 (first Bitcoin receiving address)
        node = bip32.derive_from_path(master, "m/44'/0'/0'/0/0")

        # Check expected address
        address = node.get_address()
        self.assertEqual(address, HDWalletConfig.EXPECTED_ADDR_0_0)

    def test_multiple_addresses(self):
        """Test deriving multiple addresses."""
        seed = bip32.mnemonic_to_seed(HDWalletConfig.MNEMONIC_12)
        master = bip32.master_key_from_seed(seed)

        # Derive first 3 addresses
        addresses = []
        for i in range(3):
            node = bip32.derive_from_path(master, f"m/44'/0'/0'/0/{i}")
            addresses.append(node.get_address())

        # All should be unique
        self.assertEqual(len(addresses), len(set(addresses)))

        # Check first two expected addresses
        self.assertEqual(addresses[0], HDWalletConfig.EXPECTED_ADDR_0_0)
        self.assertEqual(addresses[1], HDWalletConfig.EXPECTED_ADDR_0_1)


class TestHDWallet(unittest.TestCase):
    """Test HD Wallet functionality."""

    def test_create_hd_wallet(self):
        """Test creating HD wallet from mnemonic."""
        wallet = Wallet.from_mnemonic()

        # Check HD wallet attributes
        self.assertTrue(wallet.is_hd)
        self.assertIsNotNone(wallet.master_node)
        self.assertEqual(wallet.account_index, 0)
        self.assertEqual(wallet.external_index, 0)
        self.assertEqual(wallet.internal_index, 0)

    def test_hd_wallet_address(self):
        """Test HD wallet generates correct first address."""
        wallet = Wallet.from_mnemonic()

        # First address should match expected
        address = wallet.get_address()
        self.assertEqual(address, HDWalletConfig.EXPECTED_ADDR_0_0)

    def test_get_new_receiving_address(self):
        """Test generating new receiving addresses."""
        wallet = Wallet.from_mnemonic()

        addr1 = wallet.get_new_receiving_address()
        addr2 = wallet.get_new_receiving_address()
        addr3 = wallet.get_new_receiving_address()

        # All should be unique
        addresses = [addr1, addr2, addr3]
        self.assertEqual(len(addresses), len(set(addresses)))

        # Check indices incremented
        self.assertEqual(wallet.external_index, 3)

    def test_get_change_address(self):
        """Test generating change addresses."""
        wallet = Wallet.from_mnemonic()

        change1 = wallet.get_change_address()
        change2 = wallet.get_change_address()

        # Should be different
        self.assertNotEqual(change1, change2)

        # Check index incremented
        self.assertEqual(wallet.internal_index, 2)

        # First change address should match expected
        wallet2 = Wallet.from_mnemonic()
        change_addr = wallet2.get_change_address()
        self.assertEqual(change_addr, HDWalletConfig.EXPECTED_ADDR_1_0)

    def test_single_key_wallet_compatibility(self):
        """Test that single-key wallets still work."""
        wallet = Wallet(TestKeys.KEY1_HEX)

        # Should not be HD
        self.assertFalse(wallet.is_hd)
        self.assertIsNone(wallet.master_node)

        # Change address should be same as main address
        change = wallet.get_change_address()
        self.assertEqual(change, wallet.get_address())


class TestTransactionFees(unittest.TestCase):
    """Test transaction fee calculation and handling."""

    def test_fee_calculation(self):
        """Test automatic fee calculation."""
        # Convert WIF to hex for wallet
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        # Create transaction with manual fee rate
        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=50000,
            fee_rate=10,
            add_change=False
        )

        # Check fee was calculated
        self.assertGreater(txn.fee, 0)
        self.assertEqual(txn.fee_rate, txn.fee / txn.size_bytes)
        self.assertEqual(txn.input_value, 50000)

    def test_change_address_automatic(self):
        """Test automatic change address generation."""
        wallet = Wallet.from_mnemonic()
        txn = Transaction(wallet)

        # Create transaction with change
        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=wallet.get_address(),
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=50000,
            fee_rate=10,
            add_change=True  # Should add change output
        )

        # Should have 2 outputs (payment + change)
        self.assertEqual(len(txn.outputs), 2)

        # Change should be sent to internal chain address
        # (Can't check exact address as it increments, but should be valid)
        change_output = txn.outputs[1]
        self.assertGreater(change_output[0], 546)  # Above dust limit

    def test_dust_limit_handling(self):
        """Test that dust outputs are handled correctly."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        # Create transaction where change would be dust
        # Input: 11000, Output: 10000, Fee: ~2000 = Change: ~-1000 (negative, added to fee)
        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=12000,
            fee_rate=10,
            add_change=True
        )

        # Should not have change output (dust was added to fee)
        self.assertEqual(len(txn.outputs), 1)

    def test_fee_metadata(self):
        """Test that fee metadata is stored correctly."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=50000,
            fee_rate=10,
            add_change=False
        )

        # Check all metadata is set
        self.assertGreater(txn.size_bytes, 0)
        self.assertGreater(txn.fee, 0)
        self.assertGreater(txn.fee_rate, 0)
        self.assertEqual(txn.input_value, 50000)
        self.assertGreater(txn.output_value, 0)

        # Fee should equal input - output
        self.assertEqual(txn.fee, txn.input_value - txn.output_value)


class TestTransactionValidation(unittest.TestCase):
    """Test transaction validation before sending."""

    def test_validation_success(self):
        """Test validation passes for valid transaction."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[90000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=100000,  # Larger input so fee is reasonable percentage
            fee_rate=10,
            add_change=False
        )

        valid, msg = txn.validate_before_send()
        self.assertTrue(valid, f"Validation should pass: {msg}")

    def test_validation_unsigned(self):
        """Test validation fails for unsigned transaction."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        valid, msg = txn.validate_before_send()
        self.assertFalse(valid)
        self.assertIn("not created", msg.lower())

    def test_validation_high_fee(self):
        """Test validation warns about very high fee."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        # Create transaction with very high fee (50% of input)
        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=20000,  # Only 20k input for 10k output = 10k fee (50%)
            fee_rate=10,
            add_change=False
        )

        valid, msg = txn.validate_before_send()
        self.assertFalse(valid)
        self.assertIn("fee", msg.lower())
        self.assertIn("high", msg.lower())

    def test_validation_dust_output(self):
        """Test validation fails for dust outputs."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        txn.create(
            prev_txn_hash=TestTransactions.BLOCKCHAIN_TX_HASH,
            prev_output_index=0,
            source_address=TestKeys.TXN_TEST_ADDR,
            outputs=[[100, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],  # Dust!
            input_value=50000,  # Large input so fee percentage is reasonable
            fee_rate=10,
            add_change=False
        )

        valid, msg = txn.validate_before_send()
        self.assertFalse(valid)
        # Should fail on dust, not high fee
        self.assertIn("dust", msg.lower())

    def test_send_requires_validation(self):
        """Test that send() validates by default."""
        private_key_hex = keyUtils.wifToPrivateKey(TestKeys.TXN_TEST_WIF)
        wallet = Wallet(private_key_hex)
        txn = Transaction(wallet)

        # Don't create transaction
        with self.assertRaises(ValueError) as context:
            txn.send(skip_validation=False)

        self.assertIn("validation", str(context.exception).lower())


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
