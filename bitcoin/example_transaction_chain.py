"""
Example of chaining transactions using transaction hashes

Demonstrates how to use get_transaction_hash() to chain transactions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from config import TestKeys


def main():
    print("=" * 70)
    print("Transaction Chaining Example - Using Transaction Hashes")
    print("=" * 70)
    print()

    # Create wallet
    wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
    print(f"Wallet Address: {wallet.get_address()}")
    print()

    # Transaction 1: Spend from an existing UTXO
    print("1. Create first transaction:")
    print("-" * 70)
    txn1 = Transaction(wallet)

    signed_txn1 = txn1.create(
        prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
        prev_output_index=0,
        source_address=TestKeys.TXN_TEST_ADDR,
        outputs=[
            [30000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]
        ]
    )

    print(f"Transaction 1 created")
    print(f"Raw: {signed_txn1[:60]}...")
    print()

    # Get the hash of transaction 1
    print("2. Get transaction 1 hash (TXID):")
    print("-" * 70)
    txid1 = txn1.get_transaction_hash()
    print(f"TXID: {txid1}")
    print(f"Length: {len(txid1)} characters ({len(txid1)//2} bytes)")
    print()
    print("This TXID is the double SHA-256 hash of the raw transaction,")
    print("with bytes reversed for display (little-endian to big-endian).")
    print()

    # Explain how it would be used
    print("3. How to use TXID in next transaction:")
    print("-" * 70)
    print("If you wanted to spend output 0 of transaction 1,")
    print("you would create a new transaction like this:")
    print()
    print("  txn2 = Transaction(wallet)")
    print("  txn2.create(")
    print(f"      prev_txn_hash='{txid1}',")
    print("      prev_output_index=0,  # Spend the first output")
    print("      source_address='1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa',")
    print("      outputs=[[25000, '1SomeOtherAddress...']]")
    print("  )")
    print()

    # Show the relationship
    print("4. Transaction chain visualization:")
    print("-" * 70)
    print()
    print("  [Previous Transaction]")
    print("          |")
    print("          | Output 0: 44,321 satoshis")
    print("          |           to 133txdx...")
    print("          |")
    print("          v")
    print("  [Transaction 1]")
    print(f"    TXID: {txid1[:20]}...")
    print("    Spends: Previous TX output 0")
    print("    Creates: Output 0: 30,000 satoshis to 1KKKK...")
    print()
    print("  This output could then be spent by Transaction 2")
    print("  using TXID 1 as its prev_txn_hash")
    print()

    # Verify transaction
    print("5. Verify transaction 1:")
    print("-" * 70)
    is_valid = txn1.verify()
    print(f"Valid: {is_valid}")
    print()

    # Show raw transaction breakdown
    print("6. Transaction 1 breakdown:")
    print("-" * 70)
    print(f"Version:     {signed_txn1[:8]}")
    print(f"Input count: {signed_txn1[8:10]}")
    print(f"Prev hash:   {signed_txn1[10:74]}")
    print(f"... (full transaction is {len(signed_txn1)} chars)")
    print()

    print("=" * 70)
    print("Key Points:")
    print("- get_transaction_hash() returns the TXID")
    print("- TXID = double SHA-256 of raw transaction (reversed)")
    print("- Use TXID as prev_txn_hash to spend its outputs")
    print("- This creates a chain of transactions")
    print("=" * 70)


if __name__ == '__main__':
    main()
