# https://pypi.python.org/pypi/ecdsa/0.10
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib

from cryptography import base58Utils

# https://en.bitcoin.it/wiki/Wallet_import_format
def privateKeyToWif(key_hex):
    return base58Utils.base58CheckEncode(0x80, bytes.fromhex(key_hex))

def wifToPrivateKey(s):
    b = base58Utils.base58CheckDecode(s)
    return b.hex()

# Input is a hex-encoded, DER-encoded signature
# Output is a 64-byte hex-encoded signature
def derSigToHexSig(s):
    s, junk = ecdsa.der.remove_sequence(bytes.fromhex(s))
    if junk != b'':
        print('JUNK', junk.hex())
    assert(junk == b'')
    x, s = ecdsa.der.remove_integer(s)
    y, s = ecdsa.der.remove_integer(s)
    return '%064x%064x' % (x, y)

# Input is hex string
def privateKeyToPublicKey(s):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(s), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return (b'\04' + sk.verifying_key.to_string()).hex()

# Input is hex string
def keyToAddr(s):
    return pubKeyToAddr(privateKeyToPublicKey(s))

def pubKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(bytes.fromhex(s)).digest())
    return base58Utils.base58CheckEncode(0, ripemd160.digest())

def addrHashToScriptPubKey(b58str):
    assert(len(b58str) == 34)
    # 76     A9      14 (20 bytes)                                 88             AC
    return '76a914' + base58Utils.base58CheckDecode(b58str).hex() + '88ac'
