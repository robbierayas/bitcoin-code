"""
BIP39 Mnemonic seed phrase implementation

Implements mnemonic phrase to seed conversion according to BIP39 specification.
https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
"""

import hashlib
import hmac
import unicodedata


def mnemonic_to_seed(mnemonic, passphrase=""):
    """
    Convert BIP39 mnemonic phrase to seed using PBKDF2.

    Args:
        mnemonic (str): Space-separated mnemonic words (12, 15, 18, 21, or 24 words)
        passphrase (str): Optional passphrase for additional security (default: "")

    Returns:
        bytes: 64-byte seed derived from mnemonic

    Example:
        >>> mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
        >>> seed = mnemonic_to_seed(mnemonic)
        >>> len(seed)
        64
    """
    # Normalize mnemonic (remove extra spaces)
    mnemonic = " ".join(mnemonic.strip().split())

    # BIP39 requires Unicode NFKD normalization
    mnemonic = unicodedata.normalize('NFKD', mnemonic)
    passphrase = unicodedata.normalize('NFKD', passphrase)

    # BIP39 uses PBKDF2-HMAC-SHA512 with:
    # - Password: mnemonic (normalized)
    # - Salt: "mnemonic" + passphrase
    # - Iterations: 2048
    # - Output: 64 bytes (512 bits)

    salt = ("mnemonic" + passphrase).encode('utf-8')
    mnemonic_bytes = mnemonic.encode('utf-8')

    # Use PBKDF2 with HMAC-SHA512
    seed = hashlib.pbkdf2_hmac(
        'sha512',
        mnemonic_bytes,
        salt,
        2048,
        dklen=64
    )

    return seed


def seed_to_master_key(seed):
    """
    Convert BIP39 seed to BIP32 master private key.

    Uses HMAC-SHA512 with key "Bitcoin seed" as per BIP32 specification.

    Args:
        seed (bytes): 64-byte seed from mnemonic_to_seed()

    Returns:
        tuple: (master_private_key_hex, chain_code_hex)
            - master_private_key_hex: 32-byte private key as hex string
            - chain_code_hex: 32-byte chain code as hex string (for HD wallet derivation)

    Example:
        >>> seed = bytes.fromhex("0" * 128)  # Example seed
        >>> private_key, chain_code = seed_to_master_key(seed)
        >>> len(private_key)
        64  # 32 bytes as hex = 64 characters
    """
    # BIP32: I = HMAC-SHA512(Key = "Bitcoin seed", Data = seed)
    # Left 32 bytes = master private key
    # Right 32 bytes = chain code

    hmac_result = hmac.new(
        b"Bitcoin seed",
        seed,
        hashlib.sha512
    ).digest()

    # Split into private key (left 32 bytes) and chain code (right 32 bytes)
    master_private_key = hmac_result[:32]
    chain_code = hmac_result[32:]

    return master_private_key.hex(), chain_code.hex()


def mnemonic_to_private_key(mnemonic, passphrase=""):
    """
    Convert mnemonic phrase directly to Bitcoin private key.

    This is a convenience function that combines mnemonic_to_seed()
    and seed_to_master_key() to generate the master private key.

    Args:
        mnemonic (str): Space-separated mnemonic words
        passphrase (str): Optional passphrase (default: "")

    Returns:
        str: 32-byte private key as hex string (64 characters)

    Example:
        >>> mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
        >>> private_key = mnemonic_to_private_key(mnemonic)
        >>> len(private_key)
        64
    """
    seed = mnemonic_to_seed(mnemonic, passphrase)
    private_key, chain_code = seed_to_master_key(seed)
    return private_key


def mnemonic_to_wallet(mnemonic, passphrase=""):
    """
    Convert mnemonic phrase to wallet information (private key, WIF, address).

    Args:
        mnemonic (str): Space-separated mnemonic words
        passphrase (str): Optional passphrase (default: "")

    Returns:
        dict: Wallet information with keys:
            - 'private_key': hex private key
            - 'wif': Wallet Import Format
            - 'address': Bitcoin address
            - 'public_key': hex public key
            - 'chain_code': hex chain code (for HD derivation)

    Example:
        >>> mnemonic = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"
        >>> wallet = mnemonic_to_wallet(mnemonic)
        >>> 'address' in wallet
        True
    """
    from cryptography.keypair import KeyPair

    # Generate seed and derive keys
    seed = mnemonic_to_seed(mnemonic, passphrase)
    private_key_hex, chain_code = seed_to_master_key(seed)

    # Create KeyPair from private key
    keypair = KeyPair(private_key_hex)

    return {
        'private_key': private_key_hex,
        'wif': keypair.to_wif(),
        'address': keypair.get_address(),
        'public_key': keypair.publickey,
        'chain_code': chain_code
    }