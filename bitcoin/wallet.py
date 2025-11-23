"""
Wallet class for Bitcoin key and transaction management

Provides a higher-level interface for Bitcoin operations.
Supports both BIP39 and Electrum native seeds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import hashlib
import hmac
import unicodedata

from cryptography.keypair import KeyPair
from cryptography import bip32, base58Utils
from config import TestKeys, TestHDWallet
from bitcoin import blockchair
from bitcoin import electrum_utils


class Wallet:
    """
    Bitcoin wallet for managing keys and transactions.

    Supports both single-key and HD (hierarchical deterministic) wallets.

    Attributes:
        keypair (KeyPair): The ECDSA key pair for this wallet
        is_hd (bool): True if this is an HD wallet
        master_node (BIP32Node): Master node for HD wallet (None for single-key)
        account_index (int): BIP44 account index (default: 0)
        external_index (int): Current external (receiving) address index
        internal_index (int): Current internal (change) address index
    """

    def __init__(self, privatekeyhex=None):
        """
        Initialize Wallet with a private key.

        Args:
            privatekeyhex (str, optional): Private key as hex string (64 characters).
                                          Defaults to TestKeys.KEY3_HEX if not provided.
        """
        if privatekeyhex is None:
            privatekeyhex = TestKeys.KEY3_HEX

        # Create keypair instance variable
        self.keypair = KeyPair(privatekeyhex)

        # HD wallet properties (None for single-key wallets)
        self.is_hd = False
        self.wallet_type = 'single-key'  # 'single-key', 'bip39', or 'electrum'
        self.seed_type = None  # For Electrum: 'standard', 'segwit', etc.
        self.master_node = None
        self.account_index = 0
        self.external_index = 0  # Receiving addresses
        self.internal_index = 0  # Change addresses

        # Cache of generated addresses -> derivation paths
        # This lets us find the right key for any address we've generated
        self._address_cache = {}  # {address: (chain, index)}

    def get_address(self):
        """
        Get the Bitcoin address for this wallet.

        Returns:
            str: Bitcoin address (Base58Check encoded)
        """
        # For Electrum wallets, use compressed public keys
        if hasattr(self, 'wallet_type') and self.wallet_type == 'electrum':
            return electrum_utils.pubkey_to_address_compressed(self.keypair.publickey)
        else:
            return self.keypair.get_address()

    def get_public_key(self):
        """
        Get the public key for this wallet.

        Returns:
            str: Hex-encoded public key
        """
        return self.keypair.publickey

    def get_private_key(self):
        """
        Get the private key for this wallet.

        Returns:
            str: Hex-encoded private key
        """
        return self.keypair.get_private_key()

    def export_wif(self, compressed=False):
        """
        Export private key in WIF format.

        Args:
            compressed (bool): Whether to use compressed WIF format

        Returns:
            str: WIF-encoded private key
        """
        return self.keypair.to_wif(compressed)

    def sign_message(self, message_hash):
        """
        Sign a message hash.

        Args:
            message_hash (bytes): Hash to sign (typically SHA-256)

        Returns:
            bytes: DER-encoded signature
        """
        return self.keypair.sign(message_hash)

    def verify_message(self, message_hash, signature):
        """
        Verify a signature.

        Args:
            message_hash (bytes): Hash that was signed
            signature (bytes): DER-encoded signature

        Returns:
            bool: True if signature is valid
        """
        return self.keypair.verify(message_hash, signature)

    @classmethod
    def from_wif(cls, wif):
        """
        Create Wallet from WIF-encoded private key.

        Args:
            wif (str): WIF-encoded private key

        Returns:
            Wallet: New Wallet instance
        """
        keypair = KeyPair.from_wif(wif)
        # Create wallet with the private key
        wallet = cls(keypair.get_private_key())
        return wallet

    @classmethod
    def generate(cls):
        """
        Generate a new random Wallet.

        Returns:
            Wallet: New Wallet with random private key
        """
        keypair = KeyPair.generate()
        return cls(keypair.get_private_key())

    @classmethod
    def from_mnemonic(cls, mnemonic=None, passphrase="", account=0):
        """
        Create HD Wallet from BIP39 mnemonic seed phrase.

        Args:
            mnemonic (str, optional): BIP39 mnemonic (defaults to test mnemonic)
            passphrase (str): Optional passphrase for additional security
            account (int): BIP44 account index (default: 0)

        Returns:
            Wallet: New HD Wallet instance

        Example:
            >>> wallet = Wallet.from_mnemonic()  # Uses test mnemonic
            >>> wallet = Wallet.from_mnemonic("witch collapse practice...")
            >>> wallet.is_hd
            True
        """
        if mnemonic is None:
            mnemonic = TestHDWallet.MNEMONIC_12

        # Convert mnemonic to seed
        seed = bip32.mnemonic_to_seed(mnemonic, passphrase)

        # Generate master key
        master_node = bip32.master_key_from_seed(seed)

        # Get first receiving address (m/44'/0'/0'/0/0)
        first_node = bip32.derive_from_path(master_node, f"m/44'/0'/{account}'/0/0")

        # Create wallet with first address private key
        wallet = cls(first_node.get_private_key_hex())

        # Store HD wallet state
        wallet.is_hd = True
        wallet.wallet_type = 'bip39'
        wallet.master_node = master_node
        wallet.account_index = account
        wallet.external_index = 0
        wallet.internal_index = 0

        # Cache first address (external chain, index 0)
        first_address = first_node.get_address()
        wallet._address_cache[first_address] = (0, 0)  # (chain, index)

        return wallet

    @classmethod
    def from_electrum_seed(cls, mnemonic=None, passphrase=""):
        """
        Create HD Wallet from Electrum native seed.

        Electrum uses different derivation than BIP39:
        - PBKDF2 salt: b"electrum" + passphrase (not b"mnemonic")
        - Paths: m/0/x (receiving), m/1/x (change)
        - Uses COMPRESSED public keys for addresses

        Args:
            mnemonic (str, optional): Electrum mnemonic (defaults to test mnemonic)
            passphrase (str): Optional seed extension

        Returns:
            Wallet: New Electrum HD Wallet instance

        Example:
            >>> wallet = Wallet.from_electrum_seed()
            >>> wallet.is_hd
            True
            >>> wallet.wallet_type
            'electrum'
        """
        if mnemonic is None:
            mnemonic = TestHDWallet.MNEMONIC_12

        # Verify it's an Electrum seed
        seed_type = electrum_utils.is_electrum_seed(mnemonic)
        if not seed_type:
            raise ValueError("Not a valid Electrum seed. Use from_mnemonic() for BIP39 seeds.")

        # Convert mnemonic to seed (Electrum method)
        seed = electrum_utils.electrum_mnemonic_to_seed(mnemonic, passphrase)

        # Generate master key
        master_node = bip32.master_key_from_seed(seed)

        # Get first receiving address (m/0/0) with COMPRESSED pubkey
        first_node = bip32.derive_from_path(master_node, "m/0/0")
        first_address = electrum_utils.pubkey_to_address_compressed(
            first_node.get_keypair().publickey
        )

        # Create wallet with first address private key
        wallet = cls(first_node.get_private_key_hex())

        # Store HD wallet state
        wallet.is_hd = True
        wallet.wallet_type = 'electrum'
        wallet.seed_type = seed_type
        wallet.master_node = master_node
        wallet.account_index = 0
        wallet.external_index = 0
        wallet.internal_index = 0

        # Cache first address (external chain, index 0)
        wallet._address_cache[first_address] = (0, 0)  # (chain, index)

        return wallet

    def get_change_address(self):
        """
        Get next change address for HD wallet.

        For single-key wallets, returns the same address.
        For HD wallets, derives next address on internal chain.

        Returns:
            str: Bitcoin change address

        Example:
            >>> wallet = Wallet.from_mnemonic()
            >>> change_addr = wallet.get_change_address()
        """
        if not self.is_hd:
            # Single-key wallet - use same address for change
            return self.get_address()

        # Determine derivation path based on wallet type
        if self.wallet_type == 'electrum':
            # Electrum: m/1/x (change path)
            path = f"m/1/{self.internal_index}"
        else:
            # BIP39/BIP44: m/44'/0'/account'/1/internal_index
            path = f"m/44'/0'/{self.account_index}'/1/{self.internal_index}"

        node = bip32.derive_from_path(self.master_node, path)

        # Get address (compressed for Electrum, uncompressed for BIP39)
        if self.wallet_type == 'electrum':
            change_address = electrum_utils.pubkey_to_address_compressed(
                node.get_keypair().publickey
            )
        else:
            change_address = node.get_address()

        # Cache this address (internal chain = 1, current index)
        self._address_cache[change_address] = (1, self.internal_index)

        # Increment internal index for next time
        self.internal_index += 1

        return change_address

    def get_new_receiving_address(self):
        """
        Get next receiving address for HD wallet.

        For single-key wallets, returns the same address.
        For HD wallets, derives next address on external chain.

        Returns:
            str: Bitcoin receiving address

        Example:
            >>> wallet = Wallet.from_mnemonic()
            >>> addr1 = wallet.get_new_receiving_address()
            >>> addr2 = wallet.get_new_receiving_address()
            >>> addr1 != addr2  # True for HD wallets
        """
        if not self.is_hd:
            # Single-key wallet - always same address
            return self.get_address()

        # Determine derivation path based on wallet type
        if self.wallet_type == 'electrum':
            # Electrum: m/0/x (receiving path)
            path = f"m/0/{self.external_index}"
        else:
            # BIP39/BIP44: m/44'/0'/account'/0/external_index
            path = f"m/44'/0'/{self.account_index}'/0/{self.external_index}"

        node = bip32.derive_from_path(self.master_node, path)

        # Get address (compressed for Electrum, uncompressed for BIP39)
        if self.wallet_type == 'electrum':
            receiving_address = electrum_utils.pubkey_to_address_compressed(
                node.get_keypair().publickey
            )
        else:
            receiving_address = node.get_address()

        # Cache this address (external chain = 0, current index)
        self._address_cache[receiving_address] = (0, self.external_index)

        # Increment external index
        self.external_index += 1

        return receiving_address

    def get_private_key_for_address(self, address, auto_discover=True, search_limit=100):
        """
        Get private key for a specific address.

        For HD wallets, looks up the address in the cache and derives the key.
        If not cached and auto_discover=True, scans ahead to find the address.
        For single-key wallets, returns the wallet's private key if address matches.

        Args:
            address (str): Bitcoin address to get private key for
            auto_discover (bool): Automatically search for uncached addresses (default: True)
            search_limit (int): Maximum addresses to scan per chain if auto_discover=True (default: 100)

        Returns:
            str: Private key hex (64 characters)

        Raises:
            ValueError: If address not found or not generated by this wallet

        Example:
            >>> wallet = Wallet.from_mnemonic()
            >>> addr = wallet.get_new_receiving_address()
            >>> key = wallet.get_private_key_for_address(addr)
        """
        # Single-key wallet
        if not self.is_hd:
            if address == self.get_address():
                return self.get_private_key()
            else:
                raise ValueError(f"Address {address} does not belong to this wallet")

        # HD wallet - check cache first
        if address in self._address_cache:
            chain, index = self._address_cache[address]

            # Use appropriate derivation path based on wallet type
            if self.wallet_type == 'electrum':
                path = f"m/{chain}/{index}"
            else:
                path = f"m/44'/0'/{self.account_index}'/{chain}/{index}"

            node = bip32.derive_from_path(self.master_node, path)
            return node.get_private_key_hex()

        # If auto_discover is enabled, search for the address
        if auto_discover:
            # Search external chain (receiving addresses)
            for index in range(search_limit):
                # Use appropriate derivation path based on wallet type
                if self.wallet_type == 'electrum':
                    path = f"m/0/{index}"
                else:
                    path = f"m/44'/0'/{self.account_index}'/0/{index}"

                node = bip32.derive_from_path(self.master_node, path)

                # Get address (compressed for Electrum, uncompressed for BIP39)
                if self.wallet_type == 'electrum':
                    addr = electrum_utils.pubkey_to_address_compressed(
                        node.get_keypair().publickey
                    )
                else:
                    addr = node.get_address()

                # Cache this address
                self._address_cache[addr] = (0, index)

                if addr == address:
                    # Found it! Update external index if needed
                    if index >= self.external_index:
                        self.external_index = index + 1
                    return node.get_private_key_hex()

            # Search internal chain (change addresses)
            for index in range(search_limit):
                # Use appropriate derivation path based on wallet type
                if self.wallet_type == 'electrum':
                    path = f"m/1/{index}"
                else:
                    path = f"m/44'/0'/{self.account_index}'/1/{index}"

                node = bip32.derive_from_path(self.master_node, path)

                # Get address (compressed for Electrum, uncompressed for BIP39)
                if self.wallet_type == 'electrum':
                    addr = electrum_utils.pubkey_to_address_compressed(
                        node.get_keypair().publickey
                    )
                else:
                    addr = node.get_address()

                # Cache this address
                self._address_cache[addr] = (1, index)

                if addr == address:
                    # Found it! Update internal index if needed
                    if index >= self.internal_index:
                        self.internal_index = index + 1
                    return node.get_private_key_hex()

        # Address not found after search
        raise ValueError(
            f"Address {address} not found in first {search_limit} addresses of each chain. "
            f"It may not belong to this wallet, or you can increase search_limit parameter."
        )

    def discover_addresses(self, gap_limit=20, derivation_standard='auto'):
        """
        Discover addresses with UTXOs by scanning ahead (BIP44 gap limit).

        Checks addresses in sequence until finding gap_limit consecutive empty addresses.
        Caches all discovered addresses.

        Args:
            gap_limit (int): Number of consecutive empty addresses before stopping (default: 20)
            derivation_standard (str): Which derivation path to use:
                - 'auto': Try BIP44, then Electrum if nothing found
                - 'bip44': BIP44 standard (m/44'/0'/0'/0/x)
                - 'electrum': Electrum legacy (m/0/x)
                - 'all': Scan all standards

        Returns:
            dict: Summary of discovery {
                'external': number of external addresses found,
                'internal': number of internal addresses found,
                'total_balance': total balance in satoshis,
                'standard_used': which derivation standard found addresses
            }

        Example:
            >>> wallet = Wallet.from_mnemonic()
            >>> summary = wallet.discover_addresses()
            >>> print(f"Found {summary['external']} receiving addresses")
        """
        if not self.is_hd:
            return {'external': 1, 'internal': 0, 'total_balance': 0, 'standard_used': 'single-key'}

        print("Discovering addresses (this may take a moment)...")

        # Define derivation standards
        standards = []
        if derivation_standard == 'auto':
            # Try BIP44 first (most common), then Electrum
            standards = [
                ('BIP44', f"m/44'/0'/{self.account_index}'/0/{{}}", f"m/44'/0'/{self.account_index}'/1/{{}}"),
                ('Electrum', "m/0/{}", "m/1/{}"),
            ]
        elif derivation_standard == 'bip44':
            standards = [('BIP44', f"m/44'/0'/{self.account_index}'/0/{{}}", f"m/44'/0'/{self.account_index}'/1/{{}}")]
        elif derivation_standard == 'electrum':
            standards = [('Electrum', "m/0/{}", "m/1/{}")]
        elif derivation_standard == 'all':
            standards = [
                ('BIP44', f"m/44'/0'/{self.account_index}'/0/{{}}", f"m/44'/0'/{self.account_index}'/1/{{}}"),
                ('Electrum', "m/0/{}", "m/1/{}"),
                ('BIP49', f"m/49'/0'/{self.account_index}'/0/{{}}", f"m/49'/0'/{self.account_index}'/1/{{}}"),
                ('BIP84', f"m/84'/0'/{self.account_index}'/0/{{}}", f"m/84'/0'/{self.account_index}'/1/{{}}"),
            ]

        best_result = {'external': 0, 'internal': 0, 'total_balance': 0, 'standard_used': 'none'}

        for standard_name, external_pattern, internal_pattern in standards:
            print(f"\n=== Scanning {standard_name} ===")

            external_found = 0
            internal_found = 0
            total_balance = 0

            # Discover external chain (receiving addresses)
            gap_count = 0
            index = 0

            while gap_count < gap_limit:
                path = external_pattern.format(index)
                node = bip32.derive_from_path(self.master_node, path)
                addr = node.get_address()

                # Cache this address
                self._address_cache[addr] = (0, index)

                # Check if address has any activity (BIP44: check transaction history, not balance)
                try:
                    balance = blockchair.get_address_balance(addr)
                    # Address is "used" if it has any transaction history, even if balance is 0
                    if balance['transaction_count'] > 0:
                        external_found += 1
                        total_balance += balance['total']
                        gap_count = 0  # Reset gap counter
                        print(f"  Found external {index}: {addr} ({balance['transaction_count']} txs, {balance['total']} sats)")
                    else:
                        gap_count += 1
                except blockchair.BlockchairError:
                    # API error, assume empty
                    gap_count += 1

                index += 1

                # Safety limit
                if index > 1000:
                    print("  Reached safety limit of 1000 addresses")
                    break

            # Update external index if this is the active standard
            if external_found > 0:
                self.external_index = index

            # Discover internal chain (change addresses)
            gap_count = 0
            index = 0

            while gap_count < gap_limit:
                path = internal_pattern.format(index)
                node = bip32.derive_from_path(self.master_node, path)
                addr = node.get_address()

                # Cache this address
                self._address_cache[addr] = (1, index)

                # Check if address has any activity (BIP44: check transaction history, not balance)
                try:
                    balance = blockchair.get_address_balance(addr)
                    # Address is "used" if it has any transaction history, even if balance is 0
                    if balance['transaction_count'] > 0:
                        internal_found += 1
                        total_balance += balance['total']
                        gap_count = 0
                        print(f"  Found change {index}: {addr} ({balance['transaction_count']} txs, {balance['total']} sats)")
                    else:
                        gap_count += 1
                except blockchair.BlockchairError:
                    gap_count += 1

                index += 1

                if index > 1000:
                    print("  Reached safety limit of 1000 change addresses")
                    break

            # Update internal index if this is the active standard
            if internal_found > 0:
                self.internal_index = index

            # Track best result
            total_found = external_found + internal_found
            if total_found > 0:
                print(f"  {standard_name}: {external_found} external, {internal_found} change addresses")

                # Update best result if this standard found more addresses
                if total_found > (best_result['external'] + best_result['internal']):
                    best_result = {
                        'external': external_found,
                        'internal': internal_found,
                        'total_balance': total_balance,
                        'standard_used': standard_name
                    }

                # For 'auto' mode, stop after finding addresses with first standard
                if derivation_standard == 'auto':
                    print(f"\nUsing {standard_name} derivation standard")
                    break

        if best_result['standard_used'] == 'none':
            print("\nNo addresses found in any derivation standard")
        else:
            print(f"\nDiscovery complete ({best_result['standard_used']}): {best_result['external']} external, {best_result['internal']} change addresses")

        return best_result

    def find_utxos(self, min_confirmations=1):
        """
        Find unspent transaction outputs for this wallet's address.

        Uses Blockchair API to find UTXOs.

        Args:
            min_confirmations (int): Minimum confirmations required

        Returns:
            list: List of UTXO dictionaries (see blockchair.find_utxos())

        Raises:
            blockchair.BlockchairError: If API request fails

        Example:
            >>> wallet = Wallet()
            >>> utxos = wallet.find_utxos()
            >>> for utxo in utxos:
            ...     print(f"{utxo['txid']}:{utxo['vout']} = {utxo['value']} sats")
        """
        address = self.get_address()
        return blockchair.find_utxos(address, min_confirmations)

    def find_funding_utxo(self, min_amount=546, min_confirmations=1):
        """
        Find a suitable UTXO to fund a transaction.

        Args:
            min_amount (int): Minimum amount in satoshis (default: 546 dust limit)
            min_confirmations (int): Minimum confirmations

        Returns:
            dict or None: Best UTXO, or None if none found

        Example:
            >>> wallet = Wallet()
            >>> utxo = wallet.find_funding_utxo(min_amount=100000)
            >>> if utxo:
            ...     print(f"Can spend {utxo['value']} sats")
        """
        address = self.get_address()
        return blockchair.find_funding_utxo(address, min_amount, min_confirmations)

    def get_balance(self):
        """
        Get balance for this wallet's address.

        Uses Blockchair API.

        Returns:
            dict: Balance information (see blockchair.get_address_balance())

        Example:
            >>> wallet = Wallet()
            >>> balance = wallet.get_balance()
            >>> print(f"Balance: {balance['total']:,} satoshis")
        """
        address = self.get_address()
        return blockchair.get_address_balance(address)

    def __repr__(self):
        """String representation (doesn't expose private key)."""
        return f"Wallet(address='{self.get_address()}')"

    def __str__(self):
        """User-friendly string representation."""
        return f"Bitcoin Wallet\nAddress: {self.get_address()}\nPublic Key: {self.keypair.publickey[:20]}..."
