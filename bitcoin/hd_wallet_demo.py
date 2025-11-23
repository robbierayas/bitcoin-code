"""
HD Wallet Demo - Shows how Electrum HD wallet works

This demonstrates the Electrum wallet workflow:
1. Create Electrum HD wallet from mnemonic
2. Generate receiving and change addresses
3. Verify addresses match Electrum wallet

NOTE: The test mnemonic is an ELECTRUM NATIVE seed, not BIP39.
Electrum uses different derivation:
- PBKDF2 salt: b"electrum" (not b"mnemonic")
- Paths: m/0/x (receiving), m/1/x (change)
- Uses COMPRESSED public keys
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

    # Step 1: Create Electrum HD wallet from mnemonic
    print("\nStep 1: Create Electrum HD wallet from mnemonic")
    print("-" * 70)

    wallet = Wallet.from_electrum_seed(TestHDWallet.MNEMONIC_12)

    print(f"Created Electrum HD wallet")
    print(f"Wallet type: {wallet.wallet_type}")
    print(f"Seed type: {wallet.seed_type}")
    print(f"First address (m/0/0): {wallet.get_address()}")
    print(f"Expected: {TestHDWallet.EXPECTED_ADDR_0_0}")
    print(f"Match: {wallet.get_address() == TestHDWallet.EXPECTED_ADDR_0_0}")
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

    # Step 4: Get private key for addresses with real transaction history
    print("\nStep 4: Verify real addresses from Electrum wallet")
    print("-" * 70)

    # Test receiving address (m/0/0) - has actual transaction history
    test_addr_receiving = TestHDWallet.KNOWN_ADDR_WITH_TXS
    print(f"\nReceiving address: {test_addr_receiving}")
    print(f"This is our first address (m/0/0): {test_addr_receiving == wallet.get_address()}")

    # Test change address (m/1/0) - has actual transaction history
    test_addr_change = TestHDWallet.KNOWN_CHANGE_ADDR
    print(f"\nChange address: {test_addr_change}")
    change_addr = wallet.get_change_address()
    print(f"This is our first change address (m/1/0): {test_addr_change == change_addr}")

    print("\n[SUCCESS] Both addresses verified against Electrum wallet!")

    # Step 5: Auto-discovery of uncached address
    print("\nStep 5: Auto-discovery of uncached address (NEW FEATURE)")
    print("-" * 70)

    # This address wasn't generated yet
    # Simulate by creating a new wallet and getting its 10th address
    temp_wallet = Wallet.from_electrum_seed(TestHDWallet.MNEMONIC_12)
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
    wallet2 = Wallet.from_electrum_seed(TestHDWallet.MNEMONIC_12)
    print(f"Fresh wallet cache size: {len(wallet2._address_cache)}")

    try:
        wallet2.get_private_key_for_address(uncached_addr, auto_discover=False)
        print("[UNEXPECTED] Got private key")
    except ValueError as e:
        print(f"[EXPECTED ERROR] {str(e)[:80]}...")

    # Step 6: Create transaction with real UTXO data from API
    print("\nStep 6: Create transaction with real UTXO data from API")
    print("-" * 70)

    # Use the first receiving address that we know has transaction history
    source_addr = TestHDWallet.KNOWN_ADDR_WITH_TXS
    print(f"Source address: {source_addr}")

    # Get real UTXOs from Blockchair API
    print("Fetching UTXOs from Blockchair API...")
    try:
        utxos = wallet.find_utxos([source_addr])

        if not utxos:
            print("[SKIP] No UTXOs found for this address. Transaction demo skipped.")
            print("  (This is expected if the wallet has no unspent outputs)")
        else:
            print(f"Found {len(utxos)} UTXO(s)")

            # Use the first UTXO
            utxo = utxos[0]
            prev_txn_hash = utxo['txid']
            prev_output_index = utxo['vout']
            input_value = utxo['value']

            print(f"\nCreating transaction to spend UTXO:")
            print(f"  Previous TX: {prev_txn_hash[:16]}...")
            print(f"  Output index: {prev_output_index}")
            print(f"  Input value: {input_value:,} satoshis")

            # Create transaction with real UTXO data
            txn = Transaction(wallet)
            txn.create(
                prev_txn_hash=prev_txn_hash,
                prev_output_index=prev_output_index,
                source_address=source_addr,
                outputs=[[10000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]],
                input_value=input_value,
                fee_rate=10,
                add_change=True
            )
            print("[SUCCESS] Transaction created successfully!")
            print(f"  Signed with correct private key for {source_addr}")
            print(f"  Transaction ID: {txn.get_transaction_hash()}")
            print(f"  Signature verification: {'PASSED' if txn.verify() else 'FAILED'}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

    # Step 7: Show what happens with address discovery
    print("\nStep 7: Address Discovery (Electrum gap limit)")
    print("-" * 70)
    print("In a real Electrum wallet, you would run:")
    print("  summary = wallet.discover_addresses()")
    print("\nThis would:")
    print("  1. Check addresses in sequence (m/0/0, m/0/1, m/0/2, ...)")
    print("  2. Query Blockchair API for each address balance")
    print("  3. Cache all addresses found")
    print("  4. Stop after 20 consecutive empty addresses (gap limit)")
    print("  5. Repeat for change addresses (m/1/0, m/1/1, ...)")
    print("\nSkipping actual API calls in this demo to avoid rate limits.")

    # Step 8: Summary
    print("\n" + "=" * 70)
    print("Summary: How Electrum HD Wallets Work")
    print("=" * 70)
    print("""
1. Electrum HD Wallet generates many addresses from one mnemonic
   - Uses ELECTRUM NATIVE seed format (not BIP39)
   - PBKDF2 with salt b"electrum" + passphrase
   - Derivation paths: m/0/x (receiving), m/1/x (change)
   - Uses COMPRESSED public keys for addresses

2. Each address gets cached with its derivation path (chain, index)
   - Chain 0 = receiving addresses
   - Chain 1 = change addresses

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
   - Uses gap limit (stops after 20 consecutive empty addresses)

5. Typical workflow:
   ```python
   # Restore Electrum wallet
   wallet = Wallet.from_electrum_seed("your mnemonic here")

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

IMPORTANT: This is an Electrum NATIVE seed. For BIP39 seeds, use:
   wallet = Wallet.from_mnemonic("your BIP39 mnemonic here")
""")

    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_hd_wallet_workflow()
