"""
Base58 and Base256 encoding utilities.

Used for Bitcoin address encoding and general cryptographic purposes.
Implements Base58Check encoding as specified in Bitcoin.
"""

import hashlib

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58encode(n):
    """Encode integer to base58 string."""
    result = ''
    while n > 0:
        result = b58[n % 58] + result
        n //= 58
    return result


def base58decode(s):
    """Decode base58 string to integer."""
    result = 0
    for i in range(0, len(s)):
        result = result * 58 + b58.index(s[i])
    return result


def base256encode(n):
    """Encode integer to base256 bytes."""
    result = b''
    while n > 0:
        result = bytes([n % 256]) + result
        n //= 256
    return result


def base256decode(s):
    """Decode base256 bytes to integer."""
    result = 0
    for c in s:
        result = result * 256 + (c if isinstance(c, int) else ord(c))
    return result


def countLeadingChars(s, ch):
    """Count leading occurrences of character in string/bytes."""
    count = 0
    ch_byte = ch if isinstance(ch, int) else (ord(ch) if isinstance(ch, str) else ch)
    for c in s:
        c_byte = c if isinstance(c, int) else (ord(c) if isinstance(c, str) else c)
        if c_byte == ch_byte:
            count += 1
        else:
            break
    return count


# https://en.bitcoin.it/wiki/Base58Check_encoding
def base58CheckEncode(version, payload):
    """
    Base58Check encode with version byte and checksum.

    Args:
        version: Version byte (0x00 for Bitcoin addresses, 0x80 for WIF)
        payload: Data to encode (bytes)

    Returns:
        Base58Check encoded string
    """
    s = bytes([version]) + payload
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = s + checksum
    leadingZeros = countLeadingChars(result, 0)
    return '1' * leadingZeros + base58encode(base256decode(result))


def base58CheckDecode(s):
    """
    Base58Check decode and verify checksum.

    Args:
        s: Base58Check encoded string

    Returns:
        Decoded payload (bytes) without version byte

    Raises:
        AssertionError: If checksum verification fails
    """
    leadingOnes = countLeadingChars(s, '1')
    s = base256encode(base58decode(s))
    result = b'\0' * leadingOnes + s[:-4]
    chk = s[-4:]
    checksum = hashlib.sha256(hashlib.sha256(result).digest()).digest()[0:4]
    assert(chk == checksum)
    version = result[0]
    return result[1:]
