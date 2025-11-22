"""
Example usage of Transaction class

Demonstrates object-oriented Bitcoin transaction creation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from config import TestKeys


def main():
    print("=" * 70)
    print("Transaction Class Example - Object-Oriented Bitcoin Transactions")
    print("=" * 70)
    print()

    # Example 1: Create wallet and transaction object
    print("1. Create Wallet and Transaction:")
    print("-" * 70)
    # Use test wallet that has known test data
    wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
    print(f"Wallet Address: {wallet.get_address()}")

    transaction = Transaction(wallet)
    print(f"Transaction created: {transaction}")
    print()

    # Example 2: Create a signed transaction
    print("2. Create and sign a transaction:")
    print("-" * 70)
    # Transaction spending from previous output to new addresses
    # (This is test data from the Bitcoin blockchain)
    signed_txn = transaction.create(
        prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
        prev_output_index=0,
        source_address=TestKeys.TXN_TEST_ADDR,  # 133txdxQmwECTmXqAr9RWNHnzQ175jGb7e
        outputs=[
            [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],  # Send 24,321 satoshis
            [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]   # Send 20,000 satoshis
        ]
    )
    print(f"Signed: {transaction.signed}")
    print(f"Raw Transaction: {signed_txn[:60]}...")
    print(f"Length: {len(signed_txn)} characters")
    print()

    # Example 3: Verify transaction
    print("3. Verify transaction signature:")
    print("-" * 70)
    is_valid = transaction.verify()
    print(f"Valid: {is_valid}")
    print()

    # Example 4: Get raw transaction
    print("4. Get raw transaction hex:")
    print("-" * 70)
    raw = transaction.get_raw_transaction()
    print(f"Raw hex: {raw[:80]}...")
    print(f"Full length: {len(raw)} characters ({len(raw)//2} bytes)")
    print()

    # Example 5: Transaction breakdown
    print("5. Transaction breakdown:")
    print("-" * 70)
    print("This transaction:")
    print("  - Spends from previous transaction: c39e394d...")
    print("  - Output index: 0")
    print("  - Sends to 2 addresses:")
    print("    * 1KKKK... receives 24,321 satoshis (0.00024321 BTC)")
    print("    * 15nhZ... receives 20,000 satoshis (0.00020000 BTC)")
    print("  - Total spent: 44,321 satoshis (0.00044321 BTC)")
    print()

    # Example 6: Object representation
    print("6. Object representations:")
    print("-" * 70)
    print(f"repr(): {repr(transaction)}")
    print()
    print(f"str():")
    print(str(transaction))
    print()

    # Example 7: Creating multiple transactions with same wallet
    print("7. Multiple transactions from same wallet:")
    print("-" * 70)
    wallet2 = Wallet(TestKeys.KEY2_HEX)
    txn1 = Transaction(wallet2)
    txn2 = Transaction(wallet2)
    print(f"Transaction 1: {repr(txn1)}")
    print(f"Transaction 2: {repr(txn2)}")
    print("Note: Same wallet can create multiple transactions")
    print()

    print("=" * 70)
    print("Transaction Class Benefits:")
    print("- OOP design: Transaction object encapsulates all transaction data")
    print("- Simple API: create(), verify(), send() methods")
    print("- Wallet integration: Takes Wallet object in constructor")
    print("- Automatic signing: Handles ECDSA signing automatically")
    print("- Network ready: send() method to broadcast to Bitcoin network")
    print("=" * 70)
    print()
    print("WARNING: The send() method broadcasts to mainnet!")
    print("         Only use with test transactions or on testnet.")
    print("=" * 70)


if __name__ == '__main__':
    main()
