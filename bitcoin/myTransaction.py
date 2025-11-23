#creates address
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cryptography'))

from datetime import datetime
startTime = datetime.now()
from bitcoin import myWallet
from bitcoin.wallet import Wallet
from cryptography import ripemd160_educational as myCrypto
from rollback.rollbackRipeMD160 import myRollBack
from cryptography import base58Utils, keyUtils
from config import TestKeys
import math
import hashlib

print('')
print('')
print('MyTransaction: private key {}'.format(TestKeys.KEY3_HEX))
print('')
# Create wallet with KEY3_HEX
wallet = Wallet(TestKeys.KEY3_HEX)
# Get the keypair from wallet
keypair = wallet.keypair
# Get the public key from keypair
public_key = keypair.publickey
print('MyTransaction: public_key calculated using Wallet class {}'.format(public_key))
print('public_key type {}'.format(type(public_key)))


print('')
print('')
print('')
print('C library')
from Crypto.Hash import RIPEMD
hash = RIPEMD.new()
pkHashStep00 = hashlib.sha256(bytes.fromhex(public_key)).digest()
hash.update(pkHashStep00)
cdigest = hash.digest()
pkHashStep01 = base58Utils.base58CheckEncode(0, cdigest)
print('MyTransaction0: pkHash calculated from clib(publickey) {}'.format(pkHashStep01))
print('')

print('')
print('')
print('')
print('Method 1')
pkHash10 = wallet.get_address()
print('MyTransaction1: pkHash calculated using Wallet.get_address() {}'.format(pkHash10))

print('')
print('')
print('')
print('Method 2')
pkHashStep20 = hashlib.sha256(bytes.fromhex(public_key)).digest()
ripemd1602 = hashlib.new('ripemd160')
ripemd1602.update(pkHashStep20)
ripemd160digest = ripemd1602.digest()
pkHashStep21 = base58Utils.base58CheckEncode(0, ripemd160digest)
print('MyTransaction2: pkHash calculated from ripemd160 hashlib {}'.format(pkHashStep21))

print('')
print('')
print('')
print('Method 3')
pkHashStep30 = myCrypto.myRipeMD160(public_key, verbose=False)
pkHashStep31 = base58Utils.base58CheckEncode(0, pkHashStep30)
print('MyTransaction 3:pkHashStep31 calculated base58(RIPEMD160(SHA256(PK))) {}'.format(pkHashStep31))

print('')
print('')
print('')
print('Rollback')
myRollBack(pkHashStep31)

print('')
print(datetime.now() - startTime)