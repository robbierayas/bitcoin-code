"""
Transaction class for Bitcoin transaction management

Provides object-oriented interface for creating and sending transactions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import socket
from bitcoin import txnUtils, msgUtils, blockchair
from cryptography import keyUtils


class Transaction:
    """
    Bitcoin transaction for spending outputs.

    Attributes:
        wallet: Wallet object containing keys for signing
        raw_txn (str): Hex-encoded raw transaction (set after create())
        signed (bool): Whether transaction has been created/signed
        input_value (int): Total input value in satoshis
        output_value (int): Total output value in satoshis
        fee (int): Transaction fee in satoshis
        fee_rate (float): Actual fee rate in sat/byte
        size_bytes (int): Transaction size in bytes
        prev_txn_hash (str): Previous transaction hash
        prev_output_index (int): Previous output index
        source_address (str): Source address being spent from
        outputs (list): List of outputs

    Methods:
        create(): Create and sign transaction
        verify(): Verify transaction signature
        send(): Broadcast transaction to Bitcoin network
        _receive_chunks(): Receive and process response chunks from peer

    Example:
        wallet = Wallet.from_wif(wif)
        txn = Transaction(wallet)
        txn.create(prev_hash, 0, source_addr, outputs, fee_rate=10)
        txn.verify()
        txn.send(receive_response=True)  # Receives chunks from peer
    """

    def __init__(self, wallet):
        """
        Initialize Transaction with a wallet.

        Args:
            wallet: Wallet object to use for signing
        """
        self.wallet = wallet
        self.raw_txn = None
        self.signed = False

        # Transaction metadata
        self.input_value = 0
        self.output_value = 0
        self.fee = 0
        self.fee_rate = 0
        self.size_bytes = 0

        # Transaction details (for validation)
        self.prev_txn_hash = None
        self.prev_output_index = None
        self.source_address = None
        self.outputs = None

    def create(self, prev_txn_hash, prev_output_index, source_address, outputs,
               input_value=None, fee_rate=None, add_change=True):
        """
        Create and sign a transaction.

        Args:
            prev_txn_hash (str): Previous transaction hash (hex) to spend from
            prev_output_index (int): Output index in previous transaction to spend
            source_address (str): Bitcoin address of the output being spent
            outputs (list): List of [satoshis, destination_address] pairs
            input_value (int, optional): Value of input being spent (satoshis).
                                        If None, will be calculated from outputs + fee
            fee_rate (int, optional): Fee rate in satoshis per byte.
                                     If None, uses recommended medium fee from Blockchair
            add_change (bool): Whether to automatically add change output (default: True)

        Returns:
            str: Hex-encoded signed transaction

        Example:
            # Simple send (change handled automatically)
            outputs = [[50000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"]]
            txn = transaction.create(prev_hash, 0, source_addr, outputs,
                                    input_value=100000, fee_rate=10)

            # Manual fee (no automatic change)
            outputs = [
                [50000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
                [45000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]  # Change
            ]
            txn = transaction.create(prev_hash, 0, source_addr, outputs,
                                    input_value=100000, add_change=False)
        """
        # Store transaction details
        self.prev_txn_hash = prev_txn_hash
        self.prev_output_index = prev_output_index
        self.source_address = source_address
        self.outputs = outputs.copy()  # Store original outputs

        # Get fee rate if not provided
        if fee_rate is None:
            try:
                fees = blockchair.get_recommended_fee_rate()
                fee_rate = fees['medium']
                print(f"Using recommended fee rate: {fee_rate} sat/byte")
            except blockchair.BlockchairError:
                # Default to 10 sat/byte if API fails
                fee_rate = 10
                print(f"Warning: Could not get recommended fee. Using default: {fee_rate} sat/byte")

        # Calculate estimated transaction size
        # Base: 10 bytes (version, locktime, etc.)
        # Per input: ~148 bytes (outpoint, scriptsig, sequence)
        # Per output: ~34 bytes (value, scriptpubkey)
        num_inputs = 1
        num_outputs = len(outputs)

        # Add change output to count if needed
        if add_change:
            num_outputs += 1

        estimated_size = 10 + (num_inputs * 148) + (num_outputs * 34)

        # Calculate fee
        calculated_fee = estimated_size * fee_rate

        # Calculate output total
        output_total = sum(satoshis for satoshis, _ in outputs)

        # If input value not provided, estimate it
        if input_value is None:
            # Minimum input = outputs + fee
            input_value = output_total + calculated_fee
            print(f"Warning: input_value not provided. Estimated minimum: {input_value} satoshis")

        # Store input value
        self.input_value = input_value

        # Calculate change
        change = input_value - output_total - calculated_fee

        # Handle change output
        final_outputs = outputs.copy()

        if add_change and change > 546:  # 546 satoshis is dust limit
            # Add change output
            change_address = self.wallet.get_change_address()
            final_outputs.append([change, change_address])
            print(f"Adding change output: {change} satoshis to {change_address}")

            # Recalculate with actual number of outputs
            num_outputs = len(final_outputs)
            estimated_size = 10 + (num_inputs * 148) + (num_outputs * 34)
            calculated_fee = estimated_size * fee_rate

            # Recalculate change with updated fee
            change = input_value - output_total - calculated_fee

            if change < 546:
                # Change too small, add to fee instead
                print(f"Warning: Change {change} < dust limit. Adding to fee.")
                final_outputs = outputs.copy()  # Remove change output
                calculated_fee = input_value - output_total
            else:
                # Update change amount
                final_outputs[-1] = [change, change_address]
        elif add_change and change > 0:
            # Change is non-zero but below dust limit
            print(f"Warning: Change {change} < dust limit. Adding to fee.")
            calculated_fee += change

        # Convert outputs to format expected by makeSignedTransaction
        # [satoshis, address] -> [satoshis, scriptPubKey]
        formatted_outputs = []
        for satoshis, address in final_outputs:
            script_pubkey = keyUtils.addrHashToScriptPubKey(address)
            formatted_outputs.append([satoshis, script_pubkey])

        # Get scriptPubKey for source address (what we're spending from)
        source_script_pubkey = keyUtils.addrHashToScriptPubKey(source_address)

        # Get private key for the specific source address
        # For HD wallets, this ensures we use the correct key for that address
        try:
            private_key = self.wallet.get_private_key_for_address(source_address)
        except ValueError as e:
            raise ValueError(
                f"Cannot sign transaction: {e}\n"
                f"If using an HD wallet, make sure the source address was generated "
                f"by this wallet, or run wallet.discover_addresses() first."
            )

        # Check if this is an Electrum wallet (uses compressed keys)
        use_compressed = (hasattr(self.wallet, 'wallet_type') and
                         self.wallet.wallet_type == 'electrum')

        # Create signed transaction
        self.raw_txn = txnUtils.makeSignedTransaction(
            private_key,
            prev_txn_hash,
            prev_output_index,
            source_script_pubkey,
            formatted_outputs,
            compressed=use_compressed
        )

        # Calculate actual size and fee rate
        self.size_bytes = len(self.raw_txn) // 2  # Hex string to bytes
        self.output_value = sum(satoshis for satoshis, _ in final_outputs)
        self.fee = self.input_value - self.output_value
        self.fee_rate = self.fee / self.size_bytes if self.size_bytes > 0 else 0

        # Update outputs to reflect final state (with change if added)
        self.outputs = final_outputs

        self.signed = True

        # Print transaction summary
        print(f"\nTransaction Summary:")
        print(f"  Input:  {self.input_value:,} satoshis")
        print(f"  Output: {self.output_value:,} satoshis")
        print(f"  Fee:    {self.fee:,} satoshis")
        print(f"  Size:   {self.size_bytes} bytes")
        print(f"  Rate:   {self.fee_rate:.2f} sat/byte")

        return self.raw_txn

    def get_raw_transaction(self):
        """
        Get the raw transaction hex.

        Returns:
            str: Hex-encoded transaction or None if not created yet

        Raises:
            ValueError: If transaction not created yet
        """
        if not self.signed:
            raise ValueError("Transaction not created yet. Call create() first.")
        return self.raw_txn

    def get_transaction_hash(self):
        """
        Get the transaction hash (TXID).

        This is the double SHA-256 hash of the raw transaction, reversed.
        This hash is what would be used as prev_txn_hash in a subsequent transaction.

        Returns:
            str: Hex-encoded transaction hash (TXID)

        Raises:
            ValueError: If transaction not created yet

        Example:
            txn = Transaction(wallet)
            txn.create(prev_hash, 0, source_addr, outputs)
            txid = txn.get_transaction_hash()
            # Use txid as prev_txn_hash in next transaction
        """
        if not self.signed:
            raise ValueError("Transaction not created yet. Call create() first.")

        import hashlib

        # Double SHA-256 of raw transaction bytes
        txn_bytes = bytes.fromhex(self.raw_txn)
        hash_once = hashlib.sha256(txn_bytes).digest()
        hash_twice = hashlib.sha256(hash_once).digest()

        # Reverse byte order (little-endian to big-endian for display)
        txid = hash_twice[::-1].hex()

        return txid

    def verify(self):
        """
        Verify the transaction signature.

        Returns:
            bool: True if signature is valid

        Raises:
            ValueError: If transaction not created yet
        """
        if not self.signed:
            raise ValueError("Transaction not created yet. Call create() first.")

        try:
            txnUtils.verifyTxnSignature(self.raw_txn)
            return True
        except Exception:
            return False

    def validate_before_send(self):
        """
        Validate transaction before broadcasting.

        Checks all requirements mentioned in Bitcoin transaction best practices:
        - Transaction is signed
        - Transaction signature is valid
        - Input and output values are set
        - Fee is reasonable (not too high or too low)
        - All required fields are present

        Returns:
            tuple: (bool, str) - (is_valid, error_message)

        Example:
            >>> txn = Transaction(wallet)
            >>> txn.create(...)
            >>> valid, error = txn.validate_before_send()
            >>> if not valid:
            ...     print(f"Validation failed: {error}")
        """
        # Check if transaction is created and signed
        if not self.signed:
            return False, "Transaction not created yet. Call create() first."

        if not self.raw_txn:
            return False, "Raw transaction is empty."

        # Check if all required fields are set
        if self.prev_txn_hash is None:
            return False, "Previous transaction hash not set."

        if self.prev_output_index is None:
            return False, "Previous output index not set."

        if self.source_address is None:
            return False, "Source address not set."

        if not self.outputs:
            return False, "No outputs specified."

        # Validate signature
        try:
            if not self.verify():
                return False, "Transaction signature is invalid."
        except Exception as e:
            return False, f"Signature verification failed: {e}"

        # Check for dust outputs FIRST (before fee checks)
        for i, (satoshis, address) in enumerate(self.outputs):
            if satoshis < 546:
                return False, f"Output {i} has dust amount: {satoshis} satoshis (minimum: 546)."

        # Check input/output values
        if self.input_value <= 0:
            return False, "Input value must be positive."

        if self.output_value <= 0:
            return False, "Output value must be positive."

        if self.output_value >= self.input_value:
            return False, "Output value must be less than input value (need fee)."

        # Check fee is reasonable
        if self.fee <= 0:
            return False, "Fee must be positive."

        # Warn if fee is very high (more than 10% of input)
        if self.fee > self.input_value * 0.1:
            return False, f"Fee is very high: {self.fee} satoshis ({self.fee / self.input_value * 100:.1f}% of input). This may be a mistake."

        # Warn if fee rate is very low (less than 1 sat/byte)
        if self.fee_rate < 1:
            return False, f"Fee rate is very low: {self.fee_rate:.2f} sat/byte. Transaction may not confirm."

        # Warn if fee rate is very high (more than 1000 sat/byte)
        if self.fee_rate > 1000:
            return False, f"Fee rate is very high: {self.fee_rate:.2f} sat/byte. This may be a mistake."

        # All checks passed
        return True, "Transaction is valid."

    def send(self, peer_address="97.88.151.164", peer_port=8333, receive_response=True,
             skip_validation=False):
        """
        Send transaction to Bitcoin network.

        Validates transaction before sending unless skip_validation=True.

        Args:
            peer_address (str): Bitcoin node IP address
            peer_port (int): Bitcoin node port (default 8333)
            receive_response (bool): Whether to receive and process responses
            skip_validation (bool): Skip pre-send validation (not recommended)

        Returns:
            bool: True if sent successfully

        Raises:
            ValueError: If transaction validation fails
            RuntimeError: If network send fails

        Warning:
            This sends to mainnet! Use with caution.

        Example:
            >>> txn = Transaction(wallet)
            >>> txn.create(prev_hash, 0, source_addr, outputs, fee_rate=10)
            >>> txn.send()  # Validates before sending
        """
        # Validate before sending
        if not skip_validation:
            valid, error_msg = self.validate_before_send()
            if not valid:
                raise ValueError(f"Transaction validation failed: {error_msg}")
            print("Pre-send validation passed.")

        if not self.signed:
            raise ValueError("Transaction not created yet. Call create() first.")

        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_address, peer_port))

            # Send version message
            sock.send(msgUtils.getVersionMsg())

            # Send transaction
            txn_bytes = bytes.fromhex(self.raw_txn)
            sock.send(msgUtils.getTxMsg(txn_bytes))

            print(f"Transaction broadcast to {peer_address}:{peer_port}")
            print(f"TXID: {self.get_transaction_hash()}")

            # Receive and process response chunks if requested
            if receive_response:
                self._receive_chunks(sock)

            # Close connection
            sock.close()

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to send transaction: {e}")

    def _receive_chunks(self, sock):
        """
        Receive and process response chunks from Bitcoin network.

        Args:
            sock: Socket connection to receive from

        Note:
            This processes all incoming messages until connection closes.
        """
        import struct

        while True:
            # Receive 24-byte header
            header = sock.recv(24)
            if len(header) == 0:
                break

            # Parse header
            magic, cmd, payload_len, checksum = struct.unpack('<L12sL4s', header)

            # Receive payload in chunks
            buf = b''
            while payload_len > 0:
                chunk = sock.recv(payload_len)
                if len(chunk) == 0:
                    break
                buf += chunk
                payload_len -= len(chunk)
                print(f'Got chunk of {len(chunk)} bytes')

            # Process the message
            msgUtils.processChunk(header, buf)

    def __repr__(self):
        """String representation."""
        if self.signed:
            return f"Transaction(signed=True, txn={self.raw_txn[:40]}...)"
        else:
            return f"Transaction(signed=False, wallet={self.wallet.get_address()})"

    def __str__(self):
        """User-friendly string representation."""
        if self.signed:
            return f"Bitcoin Transaction\nSigned: True\nRaw: {self.raw_txn[:60]}...\nLength: {len(self.raw_txn)} chars"
        else:
            return f"Bitcoin Transaction\nSigned: False\nWallet: {self.wallet.get_address()}"
