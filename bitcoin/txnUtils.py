# https://pypi.python.org/pypi/ecdsa/0.10

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ecdsa
import hashlib
import struct
import unittest

from bitcoin import msgUtils
from cryptography import base58Utils, keyUtils

# Makes a transaction from the inputs
# outputs is a list of [redemptionSatoshis, outputScript]
def makeRawTransaction(outputTransactionHash, sourceIndex, scriptSig, outputs):
    def makeOutput(data):
        redemptionSatoshis, outputScript = data
        return (struct.pack("<Q", redemptionSatoshis).hex() +
        '%02x' % len(bytes.fromhex(outputScript)) + outputScript)
    formattedOutputs = ''.join(map(makeOutput, outputs))
    return (
        "01000000" + # 4 bytes version
        "01" + # varint for number of inputs
        bytes.fromhex(outputTransactionHash)[::-1].hex() + # reverse outputTransactionHash
        struct.pack('<L', sourceIndex).hex() +
        '%02x' % len(bytes.fromhex(scriptSig)) + scriptSig +
        "ffffffff" + # sequence
        "%02x" % len(outputs) + # number of outputs
        formattedOutputs +
        "00000000" # lockTime
        )

# Returns [first, sig, pub, rest]
def parseTxn(txn):
    first = txn[0:41*2]
    scriptLen = int(txn[41*2:42*2], 16)
    script = txn[42*2:42*2+2*scriptLen]
    sigLen = int(script[0:2], 16)
    sig = script[2:2+sigLen*2]
    pubLen = int(script[2+sigLen*2:2+sigLen*2+2], 16)
    pub = script[2+sigLen*2+2:]
            
    assert(len(pub) == pubLen*2)
    rest = txn[42*2+2*scriptLen:]
    return [first, sig, pub, rest]         

# Substitutes the scriptPubKey into the transaction, appends SIGN_ALL to make the version
# of the transaction that can be signed
def getSignableTxn(parsed, debug=False):
    first, sig, pub, rest = parsed

    # Handle both compressed and uncompressed public keys when deriving address
    pubkey_bytes = bytes.fromhex(pub)

    if len(pubkey_bytes) == 33 and pubkey_bytes[0] in (0x02, 0x03):
        # Compressed key - use compressed address derivation
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from bitcoin import electrum_utils
        # For compressed keys, calculate address using compressed format
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        inputAddr = ripemd160_hash

        if debug:
            # Calculate the address for debugging
            addr = base58Utils.base58CheckEncode(0x00, ripemd160_hash)
            print(f"  Reconstructed address (compressed): {addr}")
            print(f"  Reconstructed hash160: {ripemd160_hash.hex()}")
    else:
        # Uncompressed key - use standard derivation
        inputAddr = base58Utils.base58CheckDecode(keyUtils.pubKeyToAddr(pub))

        if debug:
            addr = keyUtils.pubKeyToAddr(pub)
            print(f"  Reconstructed address (uncompressed): {addr}")
            print(f"  Reconstructed hash160: {inputAddr.hex()}")

    result = first + "1976a914" + inputAddr.hex() + "88ac" + rest + "01000000"

    if debug:
        print(f"  Reconstructed scriptPubKey: 76a914{inputAddr.hex()}88ac")

    return result

# Verifies that a transaction is properly signed, assuming the generated scriptPubKey matches
# the one in the previous transaction's output
def verifyTxnSignature(txn, debug=False):
    parsed = parseTxn(txn)

    if debug:
        print(f"\nDEBUG verifyTxnSignature:")
        print(f"  Public key: {parsed[2][:40]}... (len={len(parsed[2])})")

    signableTxn = getSignableTxn(parsed, debug=debug)
    hashToSign = hashlib.sha256(hashlib.sha256(bytes.fromhex(signableTxn)).digest()).digest().hex()
    assert(parsed[1][-2:] == '01') # hashtype
    sig = keyUtils.derSigToHexSig(parsed[1][:-2])
    public_key = parsed[2]

    if debug:
        print(f"  Signable txn: {signableTxn[:80]}...")
        print(f"  Hash to sign: {hashToSign}")
        print(f"  Signature: {sig[:40]}...")

    # Handle both compressed and uncompressed public keys
    pubkey_bytes = bytes.fromhex(public_key)

    if len(pubkey_bytes) == 65 and pubkey_bytes[0] == 0x04:
        # Uncompressed key: 04 + x + y (65 bytes total)
        # Strip the 04 prefix for ecdsa library
        vk = ecdsa.VerifyingKey.from_string(pubkey_bytes[1:], curve=ecdsa.SECP256k1)
    elif len(pubkey_bytes) == 33 and pubkey_bytes[0] in (0x02, 0x03):
        # Compressed key: 02/03 + x (33 bytes total)
        # Use from_string with compressed encoding support
        vk = ecdsa.VerifyingKey.from_string(
            pubkey_bytes,
            curve=ecdsa.SECP256k1,
            validate_point=True,
            valid_encodings=("compressed",)
        )
    else:
        raise ValueError(f"Invalid public key format: length={len(pubkey_bytes)}, prefix={pubkey_bytes[0]:02x}")

    if debug:
        print(f"  Verifying...")
    assert(vk.verify_digest(bytes.fromhex(sig), bytes.fromhex(hashToSign)))

def makeSignedTransaction(privateKey, outputTransactionHash, sourceIndex, scriptPubKey, outputs, compressed=False, debug=False):
    """
    Create and sign a Bitcoin transaction.

    Args:
        privateKey (str): Private key as hex string
        outputTransactionHash (str): Hash of previous transaction
        sourceIndex (int): Output index in previous transaction
        scriptPubKey (str): Script public key of output being spent
        outputs (list): List of [satoshis, scriptPubKey] pairs
        compressed (bool): Use compressed public key format (default: False)
                          Set to True for Electrum wallets
        debug (bool): Print debug information

    Returns:
        str: Hex-encoded signed transaction
    """
    myTxn_forSig = (makeRawTransaction(outputTransactionHash, sourceIndex, scriptPubKey, outputs)
         + "01000000") # hash code

    if debug:
        print(f"\nDEBUG makeSignedTransaction:")
        print(f"  scriptPubKey: {scriptPubKey}")
        print(f"  Txn for sig: {myTxn_forSig[:80]}...")
        print(f"  Compressed: {compressed}")

    s256 = hashlib.sha256(hashlib.sha256(bytes.fromhex(myTxn_forSig)).digest()).digest()

    if debug:
        print(f"  Hash to sign: {s256.hex()}")

    sk = ecdsa.SigningKey.from_string(bytes.fromhex(privateKey), curve=ecdsa.SECP256k1)
    sig = sk.sign_digest(s256, sigencode=ecdsa.util.sigencode_der) + b'\x01' # 01 is hashtype

    # Get public key (uncompressed by default)
    pubKey = keyUtils.privateKeyToPublicKey(privateKey)

    # Convert to compressed format if needed (for Electrum wallets)
    if compressed:
        # Import here to avoid circular dependency
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from bitcoin import electrum_utils
        compressed_key = electrum_utils.get_compressed_pubkey(pubKey)
        pubKey = compressed_key.hex()

    if debug:
        print(f"  Public key: {pubKey[:40]}... (len={len(pubKey)})")

    scriptSig = msgUtils.varstr(sig).hex() + msgUtils.varstr(bytes.fromhex(pubKey)).hex()
    signed_txn = makeRawTransaction(outputTransactionHash, sourceIndex, scriptSig, outputs)
    verifyTxnSignature(signed_txn, debug=debug)
    return signed_txn
    
class TestTxnUtils(unittest.TestCase):

    def test_verifyParseTxn(self):
        txn =          ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "8a47" +
                        "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
                        "41" +
                        "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")


        parsed = parseTxn(txn)
        self.assertEqual(parsed[0], "0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000")
        self.assertEqual(parsed[1], "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01")
        self.assertEqual(parsed[2], "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55")
        self.assertEqual(parsed[3], "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

    def test_verifySignableTxn(self):
        txn =          ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "8a47" +
                        "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
                        "41" +
                        "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        parsed = parseTxn(txn)      
        myTxn_forSig = ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "1976a914" + "167c74f7491fe552ce9e1912810a984355b8ee07" + "88ac" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000" +
                        "01000000")
        signableTxn = getSignableTxn(parsed)
        self.assertEqual(signableTxn, myTxn_forSig)

    def test_verifyTxn(self):
        txn =          ("0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000" +
                        "8a47" +
                        "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01" +
                        "41" +
                        "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55" +
                        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000" +
                        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000")

        verifyTxnSignature(txn)

    def test_makeRawTransaction(self):
        #http://bitcoin.stackexchange.com/questions/3374/how-to-redeem-a-basic-tx
        txn = makeRawTransaction(
            "f2b3eb2deb76566e7324307cd47c35eeb88413f971d88519859b1834307ecfec", # output transaction hash
            1, # sourceIndex
            "76a914010966776006953d5567439e5e39f86a0d273bee88ac", # scriptSig
            [[99900000, #satoshis
            "76a914097072524438d003d23a2f23edb65aae1bb3e46988ac"]], # outputScript
            ) + "01000000" # hash code type
        self.assertEqual(txn,
            "0100000001eccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f2" +
            "010000001976a914010966776006953d5567439e5e39f86a0d273bee88acffffffff" +
            "01605af405000000001976a914097072524438d003d23a2f23edb65aae1bb3e46988ac" +
            "0000000001000000")
   
    def test_makeSignedTransaction(self):
        # Transaction from
        # https://blockchain.info/tx/901a53e7a3ca96ed0b733c0233aad15f11b0c9e436294aa30c367bf06c3b7be8
        # From 133t to 1KKKK
        privateKey = keyUtils.wifToPrivateKey("5Kb6aGpijtrb8X28GzmWtbcGZCG8jHQWFJcWugqo3MwKRvC8zyu") #133t

        signed_txn = makeSignedTransaction(privateKey,
            "c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9", # output (prev) transaction hash
            0, # sourceIndex
            keyUtils.addrHashToScriptPubKey("133txdxQmwECTmXqAr9RWNHnzQ175jGb7e"),
            [[24321, #satoshis
            keyUtils.addrHashToScriptPubKey("1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa")],
             [20000,            keyUtils.addrHashToScriptPubKey("15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7")]]
            )

        verifyTxnSignature(signed_txn)

if __name__ == '__main__':
    unittest.main()
