"""
Example of sending a transaction to the Bitcoin network

Demonstrates the Transaction.send() method with chunk receiving.

WARNING: This connects to mainnet! Only use with test transactions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from config import TestKeys


def main():
    print("=" * 70)
    print("Transaction Send Example - Broadcasting to Bitcoin Network")
    print("=" * 70)
    print()
    print("WARNING: This will attempt to connect to a Bitcoin mainnet node!")
    print("         Only proceed if you understand what this does.")
    print("=" * 70)
    print()

    # Create wallet and transaction
    print("1. Creating wallet and transaction:")
    print("-" * 70)
    wallet = Wallet.from_wif(TestKeys.TXN_TEST_WIF)
    print(f"Wallet Address: {wallet.get_address()}")

    transaction = Transaction(wallet)
    print(f"Transaction created: {transaction}")
    print()

    # Create a signed transaction (test data)
    print("2. Creating signed transaction:")
    print("-" * 70)
    signed_txn = transaction.create(
        prev_txn_hash="c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9",
        prev_output_index=0,
        source_address=TestKeys.TXN_TEST_ADDR,
        outputs=[
            [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
            [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
        ]
    )
    print(f"Transaction signed: {transaction.signed}")
    print(f"Raw: {signed_txn[:60]}...")
    print()

    # Verify before sending
    print("3. Verifying transaction:")
    print("-" * 70)
    is_valid = transaction.verify()
    print(f"Valid: {is_valid}")
    print()

    # Explain send options
    print("4. Send options:")
    print("-" * 70)
    print("The transaction.send() method has the following parameters:")
    print()
    print("  transaction.send(")
    print("      peer_address='97.88.151.164',  # Bitcoin node IP")
    print("      peer_port=8333,                # Bitcoin port (mainnet)")
    print("      receive_response=True          # Receive and process chunks")
    print("  )")
    print()
    print("When receive_response=True:")
    print("  - Receives 24-byte headers from the peer")
    print("  - Receives payload in chunks")
    print("  - Processes each chunk with msgUtils.processChunk()")
    print("  - Prints 'Got chunk of X bytes' for each chunk received")
    print()
    print("When receive_response=False:")
    print("  - Sends transaction and immediately closes connection")
    print("  - Faster but doesn't wait for confirmation from peer")
    print()

    # Don't actually send (commented out for safety)
    print("5. Actually sending (COMMENTED OUT FOR SAFETY):")
    print("-" * 70)
    print("# Uncomment the following to actually send:")
    print("# try:")
    print("#     success = transaction.send(")
    print("#         peer_address='97.88.151.164',")
    print("#         peer_port=8333,")
    print("#         receive_response=True")
    print("#     )")
    print("#     print(f'Sent successfully: {success}')")
    print("# except Exception as e:")
    print("#     print(f'Error sending: {e}')")
    print()

    print("=" * 70)
    print("IMPORTANT NOTES:")
    print("- The send() method connects to mainnet by default")
    print("- The peer address can be changed to testnet nodes")
    print("- receive_response=True will show incoming messages from the peer")
    print("- The transaction shown here is from historical blockchain data")
    print("- Do NOT send this transaction (it's already been spent!)")
    print("=" * 70)


if __name__ == '__main__':
    main()
