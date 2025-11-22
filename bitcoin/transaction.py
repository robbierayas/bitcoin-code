"""
Transaction class for Bitcoin transaction management

Provides object-oriented interface for creating and sending transactions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import socket
from bitcoin import txnUtils, msgUtils
from cryptography import keyUtils


class Transaction:
    """
    Bitcoin transaction for spending outputs.

    Attributes:
        wallet: Wallet object containing keys for signing
        raw_txn (str): Hex-encoded raw transaction (set after create())
        signed (bool): Whether transaction has been created/signed

    Methods:
        create(): Create and sign transaction
        verify(): Verify transaction signature
        send(): Broadcast transaction to Bitcoin network
        _receive_chunks(): Receive and process response chunks from peer

    Example:
        wallet = Wallet.from_wif(wif)
        txn = Transaction(wallet)
        txn.create(prev_hash, 0, source_addr, outputs)
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

    def create(self, prev_txn_hash, prev_output_index, source_address, outputs):
        """
        Create and sign a transaction.

        Args:
            prev_txn_hash (str): Previous transaction hash (hex) to spend from
            prev_output_index (int): Output index in previous transaction to spend
            source_address (str): Bitcoin address of the output being spent
            outputs (list): List of [satoshis, destination_address] pairs

        Returns:
            str: Hex-encoded signed transaction

        Example:
            outputs = [
                [50000, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
                [25000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
            ]
            txn = transaction.create(prev_hash, 0, source_addr, outputs)
        """
        # Convert outputs to format expected by makeSignedTransaction
        # [satoshis, address] -> [satoshis, scriptPubKey]
        formatted_outputs = []
        for satoshis, address in outputs:
            script_pubkey = keyUtils.addrHashToScriptPubKey(address)
            formatted_outputs.append([satoshis, script_pubkey])

        # Get scriptPubKey for source address (what we're spending from)
        source_script_pubkey = keyUtils.addrHashToScriptPubKey(source_address)

        # Get private key from wallet
        private_key = self.wallet.get_private_key()

        # Create signed transaction
        self.raw_txn = txnUtils.makeSignedTransaction(
            private_key,
            prev_txn_hash,
            prev_output_index,
            source_script_pubkey,
            formatted_outputs
        )

        self.signed = True
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

    def send(self, peer_address="97.88.151.164", peer_port=8333, receive_response=True):
        """
        Send transaction to Bitcoin network.

        Args:
            peer_address (str): Bitcoin node IP address
            peer_port (int): Bitcoin node port (default 8333)
            receive_response (bool): Whether to receive and process responses

        Returns:
            bool: True if sent successfully

        Raises:
            ValueError: If transaction not created yet

        Warning:
            This sends to mainnet! Use with caution.
        """
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
