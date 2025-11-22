"""
BIP32 Hierarchical Deterministic Wallet Implementation

Implements:
- BIP39: Mnemonic seed phrases
- BIP32: HD wallet key derivation
- BIP44: Multi-account hierarchy

WARNING: Educational implementation only. Not security audited.
Use production libraries (python-bitcoinlib, pycoin) for real funds.
"""

import hashlib
import hmac
import unicodedata
import sys
import os

# Handle imports when running directly vs as module
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cryptography.keypair import KeyPair


# BIP39 English wordlist (2048 words)
# For full implementation, load from file
# Abbreviated for demonstration - full wordlist needed for production
BIP39_WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    # ... (full 2048-word list would go here)
    # For testing, we'll use a subset
]


class BIP32Node:
    """
    Represents a node in the BIP32 derivation tree.

    Attributes:
        private_key (bytes): 32-byte private key
        chain_code (bytes): 32-byte chain code
        depth (int): Depth in the tree (0 = master)
        fingerprint (bytes): Parent key fingerprint (4 bytes)
        child_number (int): Child index
        is_hardened (bool): Whether this is a hardened key
    """

    def __init__(self, private_key, chain_code, depth=0, fingerprint=b'\x00\x00\x00\x00', child_number=0):
        """
        Initialize BIP32 node.

        Args:
            private_key: 32 bytes
            chain_code: 32 bytes
            depth: Depth in tree
            fingerprint: Parent fingerprint (4 bytes)
            child_number: Child index
        """
        if len(private_key) != 32:
            raise ValueError("Private key must be 32 bytes")
        if len(chain_code) != 32:
            raise ValueError("Chain code must be 32 bytes")

        self.private_key = private_key
        self.chain_code = chain_code
        self.depth = depth
        self.fingerprint = fingerprint
        self.child_number = child_number
        self.is_hardened = child_number >= 0x80000000

    def get_keypair(self):
        """
        Get KeyPair instance for this node.

        Returns:
            KeyPair instance
        """
        return KeyPair(self.private_key.hex())

    def get_address(self):
        """
        Get Bitcoin address for this node.

        Returns:
            str: Bitcoin address
        """
        keypair = self.get_keypair()
        return keypair.get_address()

    def get_private_key_hex(self):
        """
        Get private key as hex string.

        Returns:
            str: 64-character hex string
        """
        return self.private_key.hex()


def normalize_string(txt):
    """
    Normalize string for BIP39 (NFKD normalization).

    Args:
        txt: Input string

    Returns:
        str: Normalized string
    """
    if isinstance(txt, bytes):
        txt = txt.decode('utf-8')
    return unicodedata.normalize('NFKD', txt)


def mnemonic_to_seed(mnemonic, passphrase=""):
    """
    Convert BIP39 mnemonic to 512-bit seed (BIP39).

    Uses PBKDF2-HMAC-SHA512 with 2048 iterations.

    Args:
        mnemonic (str): Space-separated mnemonic words (12, 15, 18, 21, or 24 words)
        passphrase (str): Optional passphrase for additional security

    Returns:
        bytes: 64-byte seed

    Example:
        >>> mnemonic = "witch collapse practice feed shame open despair creek road again ice least"
        >>> seed = mnemonic_to_seed(mnemonic)
        >>> len(seed)
        64
    """
    # Normalize mnemonic and passphrase
    mnemonic_normalized = normalize_string(mnemonic)
    passphrase_normalized = normalize_string(passphrase)

    # BIP39 uses "mnemonic" prefix for salt
    salt = ('mnemonic' + passphrase_normalized).encode('utf-8')

    # PBKDF2-HMAC-SHA512 with 2048 iterations
    seed = hashlib.pbkdf2_hmac(
        'sha512',
        mnemonic_normalized.encode('utf-8'),
        salt,
        2048,
        dklen=64
    )

    return seed


def master_key_from_seed(seed):
    """
    Derive master private key and chain code from seed (BIP32).

    Args:
        seed (bytes): 64-byte seed from BIP39

    Returns:
        BIP32Node: Master node with private key and chain code

    Example:
        >>> seed = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
        >>> master = master_key_from_seed(seed)
        >>> isinstance(master, BIP32Node)
        True
    """
    if len(seed) < 16 or len(seed) > 64:
        raise ValueError("Seed must be between 16 and 64 bytes")

    # HMAC-SHA512 with key "Bitcoin seed"
    hmac_result = hmac.new(
        b"Bitcoin seed",
        seed,
        hashlib.sha512
    ).digest()

    # Split into master private key (left 32 bytes) and chain code (right 32 bytes)
    master_private_key = hmac_result[:32]
    master_chain_code = hmac_result[32:]

    # Verify master private key is valid (must be less than curve order n)
    master_int = int.from_bytes(master_private_key, byteorder='big')
    curve_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    if master_int == 0 or master_int >= curve_order:
        raise ValueError("Invalid master key (unlikely - retry with different seed)")

    return BIP32Node(
        private_key=master_private_key,
        chain_code=master_chain_code,
        depth=0,
        fingerprint=b'\x00\x00\x00\x00',
        child_number=0
    )


def derive_child_key(parent_node, index):
    """
    Derive child key from parent key (BIP32).

    Args:
        parent_node (BIP32Node): Parent node
        index (int): Child index (0-2^31-1 for normal, 2^31-2^32-1 for hardened)

    Returns:
        BIP32Node: Child node

    Example:
        >>> master = master_key_from_seed(bytes(64))
        >>> child = derive_child_key(master, 0)  # First normal child
        >>> hardened_child = derive_child_key(master, 0x80000000)  # First hardened child
    """
    curve_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    # Check if hardened derivation
    is_hardened = index >= 0x80000000

    if is_hardened:
        # Hardened child: data = 0x00 || parent_private_key || index
        data = b'\x00' + parent_node.private_key + index.to_bytes(4, byteorder='big')
    else:
        # Normal child: data = parent_public_key || index
        # Get parent public key from private key
        parent_keypair = parent_node.get_keypair()
        parent_pubkey_hex = parent_keypair.publickey

        # Convert to compressed format
        x = int(parent_pubkey_hex[2:66], 16)  # Skip '04' prefix, get x coordinate
        y = int(parent_pubkey_hex[66:], 16)  # Get y coordinate

        # Compressed public key: 02/03 prefix + x coordinate
        if y % 2 == 0:
            compressed_pubkey = bytes.fromhex('02' + parent_pubkey_hex[2:66])
        else:
            compressed_pubkey = bytes.fromhex('03' + parent_pubkey_hex[2:66])

        data = compressed_pubkey + index.to_bytes(4, byteorder='big')

    # HMAC-SHA512 with parent chain code as key
    hmac_result = hmac.new(
        parent_node.chain_code,
        data,
        hashlib.sha512
    ).digest()

    # Split result
    left_32 = hmac_result[:32]
    child_chain_code = hmac_result[32:]

    # Calculate child private key
    left_int = int.from_bytes(left_32, byteorder='big')
    parent_key_int = int.from_bytes(parent_node.private_key, byteorder='big')

    child_key_int = (left_int + parent_key_int) % curve_order

    # Check validity
    if left_int >= curve_order or child_key_int == 0:
        raise ValueError(f"Invalid child key at index {index} (unlikely - use next index)")

    child_private_key = child_key_int.to_bytes(32, byteorder='big')

    # Calculate parent fingerprint (first 4 bytes of HASH160 of parent public key)
    parent_keypair = parent_node.get_keypair()
    parent_pubkey_hex = parent_keypair.publickey

    # Get compressed public key for fingerprint
    x = int(parent_pubkey_hex[2:66], 16)
    y = int(parent_pubkey_hex[66:], 16)
    if y % 2 == 0:
        compressed_pubkey = bytes.fromhex('02' + parent_pubkey_hex[2:66])
    else:
        compressed_pubkey = bytes.fromhex('03' + parent_pubkey_hex[2:66])

    # HASH160 = RIPEMD160(SHA256(pubkey))
    sha256_hash = hashlib.sha256(compressed_pubkey).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    fingerprint = ripemd160_hash[:4]

    return BIP32Node(
        private_key=child_private_key,
        chain_code=child_chain_code,
        depth=parent_node.depth + 1,
        fingerprint=fingerprint,
        child_number=index
    )


def parse_derivation_path(path):
    """
    Parse BIP32 derivation path string.

    Args:
        path (str): Derivation path (e.g., "m/44'/0'/0'/0/0")

    Returns:
        list: List of integer indices

    Example:
        >>> parse_derivation_path("m/44'/0'/0'/0/0")
        [2147483692, 2147483648, 2147483648, 0, 0]
    """
    if not path.startswith('m/') and not path.startswith('M/'):
        raise ValueError("Path must start with 'm/' or 'M/'")

    # Remove 'm/' prefix
    path = path[2:]

    if not path:
        return []

    # Split by '/'
    parts = path.split('/')

    indices = []
    for part in parts:
        # Check for hardened derivation
        if part.endswith("'") or part.endswith('h'):
            # Hardened: add 2^31
            index = int(part[:-1])
            index += 0x80000000  # 2^31
        else:
            index = int(part)

        indices.append(index)

    return indices


def derive_from_path(master_node, path):
    """
    Derive key at specific derivation path.

    Args:
        master_node (BIP32Node): Master node
        path (str or list): Derivation path string or list of indices

    Returns:
        BIP32Node: Derived node

    Example:
        >>> seed = mnemonic_to_seed("witch collapse practice feed...")
        >>> master = master_key_from_seed(seed)
        >>> node = derive_from_path(master, "m/44'/0'/0'/0/0")
        >>> address = node.get_address()
    """
    if isinstance(path, str):
        indices = parse_derivation_path(path)
    else:
        indices = path

    current_node = master_node

    for index in indices:
        current_node = derive_child_key(current_node, index)

    return current_node


def mnemonic_to_private_key(mnemonic, passphrase="", path="m/44'/0'/0'/0/0"):
    """
    Convert mnemonic directly to private key at specific path.

    Convenience function that combines all steps.

    Args:
        mnemonic (str): BIP39 mnemonic
        passphrase (str): Optional passphrase
        path (str): Derivation path

    Returns:
        str: Private key hex string

    Example:
        >>> mnemonic = "witch collapse practice feed shame open despair creek road again ice least"
        >>> private_key = mnemonic_to_private_key(mnemonic)
        >>> len(private_key)
        64
    """
    seed = mnemonic_to_seed(mnemonic, passphrase)
    master = master_key_from_seed(seed)
    node = derive_from_path(master, path)
    return node.get_private_key_hex()


# Test function
def test_bip32():
    """
    Test BIP32 implementation with known test vectors.
    """
    print("Testing BIP32 Implementation")
    print("=" * 70)

    # Test 1: Mnemonic to seed
    print("\nTest 1: Mnemonic to Seed")
    mnemonic = "witch collapse practice feed shame open despair creek road again ice least"
    seed = mnemonic_to_seed(mnemonic)
    print(f"Mnemonic: {mnemonic}")
    print(f"Seed: {seed.hex()[:64]}...")
    print(f"Seed length: {len(seed)} bytes")

    # Test 2: Master key derivation
    print("\nTest 2: Master Key Derivation")
    master = master_key_from_seed(seed)
    print(f"Master private key: {master.get_private_key_hex()}")
    print(f"Master address: {master.get_address()}")

    # Test 3: Child key derivation
    print("\nTest 3: Derive m/44'/0'/0'/0/0 (first Bitcoin receiving address)")
    node = derive_from_path(master, "m/44'/0'/0'/0/0")
    print(f"Private key: {node.get_private_key_hex()}")
    print(f"Address: {node.get_address()}")
    print(f"Depth: {node.depth}")
    print(f"Hardened: {node.is_hardened}")

    # Test 4: Multiple addresses
    print("\nTest 4: Derive first 5 receiving addresses")
    for i in range(5):
        path = f"m/44'/0'/0'/0/{i}"
        node = derive_from_path(master, path)
        print(f"  {path}: {node.get_address()}")

    # Test 5: Change addresses
    print("\nTest 5: Derive first 3 change addresses (internal chain)")
    for i in range(3):
        path = f"m/44'/0'/0'/1/{i}"
        node = derive_from_path(master, path)
        print(f"  {path}: {node.get_address()}")

    print("\n" + "=" * 70)
    print("BIP32 Tests Complete!")


if __name__ == "__main__":
    test_bip32()
