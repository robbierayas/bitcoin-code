"""
HD Wallet Demo - Shows how address discovery and transaction signing works

This demonstrates the complete workflow:
1. Create HD wallet from mnemonic
2. Discover addresses with UTXOs
3. Create transaction from the correct address
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bitcoin.wallet import Wallet
from bitcoin.transaction import Transaction
from config import TestHDWallet


def demo_hd_wallet_workflow():
    """
    Demonstrate the complete HD wallet workflow.
    """
    print("=" * 70)
    print("HD Wallet Address Discovery and Transaction Signing Demo")
    print("=" * 70)

    # Step 1: Create HD wallet from mnemonic
    print("\nStep 1: Create HD wallet from mnemonic")
    print("-" * 70)

    wallet = Wallet.from_mnemonic(TestHDWallet.MNEMONIC_12)

    print(f"Created HD wallet")
    print(f"First address: {wallet.get_address()}")
    print(f"Is HD wallet: {wallet.is_hd}")

    # Step 2: Generate additional addresses
    print("\nStep 2: Generate receiving addresses")
    print("-" * 70)

    addresses = []
    for i in range(3):
        addr = wallet.get_new_receiving_address()
        addresses.append(addr)
        print(f"  Address {i+1}: {addr}")

    # Step 3: Show address cache
    print("\nStep 3: Address cache (what the wallet knows about)")
    print("-" * 70)
    print(f"Cached addresses: {len(wallet._address_cache)}")
    for addr, (chain, index) in wallet._address_cache.items():
        chain_name = "external" if chain == 0 else "internal"
        print(f"  {addr[:20]}... -> {chain_name} chain, index {index}")

    # Step 4: Show how to get private key for specific address
    print("\nStep 4: Get private key for specific address")
    print("-" * 70)

    test_addr = addresses[1]  # Second address we generated
    print(f"Address: {test_addr}")

    try:
        private_key = wallet.get_private_key_for_address(test_addr)
        print(f"Private key: {private_key[:20]}...")
        print("[SUCCESS] Retrieved private key")
    except ValueError as e:
        print(f"[ERROR] {e}")

    # Step 5: Auto-discovery of uncached address
    print("\nStep 5: Auto-discovery of uncached address (NEW FEATURE)")
    print("-" * 70)

    # This address wasn't generated yet
    # Simulate by creating a new wallet and getting its 10th address
    temp_wallet = Wallet.from_mnemonic(TestHDWallet.MNEMONIC_12)
    for _ in range(10):
        temp_wallet.get_new_receiving_address()
    uncached_addr = temp_wallet.get_new_receiving_address()  # 11th address (index 10)

    print(f"Trying to get key for uncached address: {uncached_addr}")
    print(f"This is address index 10, which is NOT in our cache yet")
    print(f"Current cache size: {len(wallet._address_cache)}")

    try:
        # With auto_discover=True (default), this will scan ahead and find it
        private_key = wallet.get_private_key_for_address(uncached_addr)
        print(f"[SUCCESS] Auto-discovery found the address!")
        print(f"Private key: {private_key[:20]}...")
        print(f"Cache size after auto-discovery: {len(wallet._address_cache)}")
    except ValueError as e:
        print(f"[ERROR] {str(e)[:80]}...")

    # Step 5b: Try with auto_discover disabled
    print("\nStep 5b: Same address with auto_discover=False (should fail)")
    print("-" * 70)

    # Create fresh wallet to test
    wallet2 = Wallet.from_mnemonic(TestHDWallet.MNEMONIC_12)
    print(f"Fresh wallet cache size: {len(wallet2._address_cache)}")

    try:
        wallet2.get_private_key_for_address(uncached_addr, auto_discover=False)
        print("[UNEXPECTED] Got private key")
    except ValueError as e:
        print(f"[EXPECTED ERROR] {str(e)[:80]}...")

    # Step 6: Create transaction from cached address
    print("\nStep 6: Create transaction from cached address")
    print("-" * 70)

    # Simulate having a UTXO at addresses[0]
    source_addr = addresses[0]
    print(f"Source address: {source_addr}")
    print(f"Creating transaction to spend from this address...")

    try:
        txn = Transaction(wallet)
        txn.create(
            prev_txn_hash="a" * 64,  # Dummy transaction hash
            prev_output_index=0,
            source_address=source_addr,  # Wallet knows the key for this!
            outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
            input_value=50000,
            fee_rate=10,
            add_change=True
        )
        print("[SUCCESS] Transaction created successfully!")
        print(f"  Transaction uses correct private key for {source_addr}")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Step 7: Show what happens with address discovery
    print("\nStep 7: Address Discovery (BIP44 gap limit)")
    print("-" * 70)
    print("In a real wallet, you would run:")
    print("  summary = wallet.discover_addresses()")
    print("\nThis would:")
    print("  1. Check addresses in sequence (m/44'/0'/0'/0/0, 0/1, 0/2, ...)")
    print("  2. Query Blockchair API for each address balance")
    print("  3. Cache all addresses found")
    print("  4. Stop after 20 consecutive empty addresses (gap limit)")
    print("\nSkipping actual API calls in this demo to avoid rate limits.")

    # Step 8: Summary
    print("\n" + "=" * 70)
    print("Summary: How It All Works Together")
    print("=" * 70)
    print("""
1. HD Wallet generates many addresses from one mnemonic
2. Each address gets cached with its derivation path (chain, index)
3. When creating a transaction:
   - You specify the source_address (where the UTXO is)
   - Wallet looks up that address in the cache (or auto-discovers it)
   - Auto-discovery scans up to 100 addresses per chain by default
   - Derives the correct private key for that specific address
   - Signs the transaction with the right key

4. For address discovery:
   - AUTOMATIC: get_private_key_for_address() auto-discovers by default
   - MANUAL: Run wallet.discover_addresses() after restoring from mnemonic
   - Manual discovery scans ahead and caches all addresses with UTXOs
   - Uses BIP44 gap limit (stops after 20 consecutive empty addresses)

5. Typical workflow:
   ```python
   # Restore wallet
   wallet = Wallet.from_mnemonic("your mnemonic here")

   # Discover all addresses with funds
   summary = wallet.discover_addresses()
   print(f"Found {summary['total_balance']} satoshis")

   # Find UTXOs
   utxos = wallet.find_utxos()

   # Create transaction (wallet automatically uses correct key)
   for utxo in utxos:
       txn = Transaction(wallet)
       txn.create(
           prev_txn_hash=utxo['txid'],
           prev_output_index=utxo['vout'],
           source_address=... # Address that owns this UTXO
           outputs=[...],
           input_value=utxo['value']
       )
   ```
""")

    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_hd_wallet_workflow()
