# https://pypi.python.org/pypi/ecdsa/0.10
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib

from cryptography import base58Utils
from cryptography.keypair import KeyPair

# ============================================================================
# LEGACY FUNCTION-BASED API (maintained for backward compatibility)
# ============================================================================
# Note: These functions now use the KeyPair class internally.
# For new code, use KeyPair class directly for better OOP design.

# https://en.bitcoin.it/wiki/Wallet_import_format
def privateKeyToWif(key_hex):
    """
    Convert private key to WIF format.

    Args:
        key_hex (str): Private key as hex string

    Returns:
        str: WIF-encoded private key
    """
    keypair = KeyPair(key_hex)
    return keypair.to_wif()

def wifToPrivateKey(s):
    """
    Convert WIF to private key hex.

    Args:
        s (str): WIF-encoded private key

    Returns:
        str: Private key as hex string
    """
    keypair = KeyPair.from_wif(s)
    return keypair.get_private_key()

def privateKeyToPublicKey(s):
    """
    Generate public key from private key.

    Args:
        s (str): Private key as hex string

    Returns:
        str: Public key as hex string (uncompressed)
    """
    keypair = KeyPair(s)
    return keypair.publickey

def keyToAddr(s):
    """
    Generate Bitcoin address from private key.

    Args:
        s (str): Private key as hex string

    Returns:
        str: Bitcoin address (Base58Check encoded)
    """
    keypair = KeyPair(s)
    return keypair.get_address()

def pubKeyToAddr(s):
    """
    Generate Bitcoin address from public key.

    Args:
        s (str): Public key as hex string

    Returns:
        str: Bitcoin address (Base58Check encoded)
    """
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(bytes.fromhex(s)).digest())
    return base58Utils.base58CheckEncode(0, ripemd160.digest())

# ============================================================================
# UTILITY FUNCTIONS (not part of KeyPair class)
# ============================================================================

def derSigToHexSig(s):
    """
    Convert DER-encoded signature to hex signature.

    Args:
        s (str): DER-encoded signature (hex string)

    Returns:
        str: 64-byte hex-encoded signature
    """
    s, junk = ecdsa.der.remove_sequence(bytes.fromhex(s))
    if junk != b'':
        print('JUNK', junk.hex())
    assert(junk == b'')
    x, s = ecdsa.der.remove_integer(s)
    y, s = ecdsa.der.remove_integer(s)
    return '%064x%064x' % (x, y)

def addrHashToScriptPubKey(b58str):
    """
    Convert Bitcoin address to scriptPubKey.

    Args:
        b58str (str): Bitcoin address (34 characters)

    Returns:
        str: scriptPubKey as hex string
    """
    assert(len(b58str) == 34)
    # 76     A9      14 (20 bytes)                                 88             AC
    return '76a914' + base58Utils.base58CheckDecode(b58str).hex() + '88ac'
