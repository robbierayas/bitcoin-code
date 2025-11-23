"""
Electrum Wallet Utilities

Helper functions for Electrum native seed support.
Electrum uses different derivation than BIP39:
- PBKDF2 salt: b"electrum" + passphrase (not b"mnemonic")
- Derivation paths: m/0/x (receiving), m/1/x (change)
- Uses COMPRESSED public keys for addresses
"""

import hashlib
import hmac
import unicodedata
from cryptography import base58Utils


# Electrum seed version prefixes
ELECTRUM_SEED_PREFIXES = {
    '01': 'standard',  # P2PKH (starts with '1')
    '100': 'segwit',   # P2WPKH (bech32)
    '101': '2fa_segwit',
    '102': '2fa',
}


def normalize_electrum_text(text):
    """
    Normalize text exactly like Electrum does.

    Uses NFKD normalization and normalizes whitespace.
    """
    text = unicodedata.normalize('NFKD', text)
    return ' '.join(text.split())


def is_electrum_seed(mnemonic):
    """
    Check if mnemonic is an Electrum native seed.

    Electrum seeds are validated using HMAC-SHA512 with key "Seed version".
    The hash must start with a known version prefix.

    Args:
        mnemonic (str): Mnemonic to check

    Returns:
        str or None: Seed type ('standard', 'segwit', etc.) or None if not Electrum
    """
    normalized = normalize_electrum_text(mnemonic)
    h = hmac.new(b"Seed version", normalized.encode('utf8'), hashlib.sha512)
    seed_hash = h.hexdigest()

    for prefix, seed_type in ELECTRUM_SEED_PREFIXES.items():
        if seed_hash.startswith(prefix):
            return seed_type

    return None


def electrum_mnemonic_to_seed(mnemonic, passphrase=''):
    """
    Convert Electrum mnemonic to seed using Electrum's method.

    Uses PBKDF2-HMAC-SHA512 with:
    - 2048 iterations
    - Salt: b"electrum" + passphrase (NOT b"mnemonic" like BIP39)

    Args:
        mnemonic (str): Electrum mnemonic
        passphrase (str): Optional passphrase (seed extension)

    Returns:
        bytes: 64-byte seed
    """
    mnemonic = normalize_electrum_text(mnemonic)
    passphrase = normalize_electrum_text(passphrase) if passphrase else ''

    salt = b'electrum' + passphrase.encode('utf-8')
    seed = hashlib.pbkdf2_hmac(
        'sha512',
        mnemonic.encode('utf-8'),
        salt,
        2048
    )
    return seed


def get_compressed_pubkey(uncompressed_hex):
    """
    Convert uncompressed public key to compressed format.

    Args:
        uncompressed_hex (str): Uncompressed pubkey (130 hex chars, starts with 04)

    Returns:
        bytes: Compressed public key (33 bytes)
    """
    if len(uncompressed_hex) != 130:
        raise ValueError("Uncompressed public key must be 130 hex characters")

    x = int(uncompressed_hex[2:66], 16)
    y = int(uncompressed_hex[66:], 16)

    # Compressed format: 02 or 03 prefix + x coordinate
    prefix = '02' if y % 2 == 0 else '03'
    return bytes.fromhex(prefix + uncompressed_hex[2:66])


def pubkey_to_address_compressed(pubkey_hex):
    """
    Generate Bitcoin address from public key using COMPRESSED format.

    This is what Electrum uses for standard wallets.

    Args:
        pubkey_hex (str): Public key (uncompressed 130 hex chars)

    Returns:
        str: Bitcoin address (P2PKH, starts with '1')
    """
    # Convert to compressed
    compressed = get_compressed_pubkey(pubkey_hex)

    # Hash160 (SHA256 then RIPEMD160)
    sha256_hash = hashlib.sha256(compressed).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # Base58Check encode with version 0x00 (P2PKH mainnet)
    return base58Utils.base58CheckEncode(0x00, ripemd160_hash)


def get_electrum_master_xpub(master_node):
    """
    Generate master xpub in Electrum format.

    Args:
        master_node: BIP32Node master key

    Returns:
        str: xpub string
    """
    # Version bytes for mainnet xpub
    version = bytes.fromhex('0488B21E')

    # Master key details
    depth = master_node.depth.to_bytes(1, 'big')
    parent_fp = master_node.fingerprint
    child_num = master_node.child_number.to_bytes(4, 'big')
    chain_code = master_node.chain_code

    # Get compressed public key
    keypair = master_node.get_keypair()
    compressed = get_compressed_pubkey(keypair.publickey)

    # Concatenate and checksum
    xpub_bytes = version + depth + parent_fp + child_num + chain_code + compressed
    checksum = hashlib.sha256(hashlib.sha256(xpub_bytes).digest()).digest()[:4]
    xpub_with_checksum = xpub_bytes + checksum

    # Base58 encode
    xpub_int = int.from_bytes(xpub_with_checksum, 'big')
    xpub = base58Utils.base58encode(xpub_int)

    # Add leading '1's for leading zero bytes
    leading_zeros = len(xpub_with_checksum) - len(xpub_with_checksum.lstrip(b'\x00'))
    xpub = '1' * leading_zeros + xpub

    return xpub


def get_electrum_root_fingerprint(master_node):
    """
    Calculate BIP32 root fingerprint (first 4 bytes of HASH160 of master pubkey).

    Args:
        master_node: BIP32Node master key

    Returns:
        str: 8-character hex fingerprint
    """
    keypair = master_node.get_keypair()
    compressed = get_compressed_pubkey(keypair.publickey)

    # HASH160 and take first 4 bytes
    sha256_hash = hashlib.sha256(compressed).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    return ripemd160_hash[:4].hex()
