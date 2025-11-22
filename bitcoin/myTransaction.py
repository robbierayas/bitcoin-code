#creates address
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cryptography'))

from datetime import datetime
startTime = datetime.now()
from bitcoin import myWallet
from cryptography import ripemd160_educational as myCrypto
from cryptography.rollback import myRollBack
from cryptography import base58Utils, keyUtils
from config import TestKeys
import math
import hashlib

print('')
print('')
print('MyTransaction: private key {}'.format(TestKeys.KEY3_HEX))
print('')
public_key = myWallet.createAddress(TestKeys.KEY3_HEX)
print('MyTransaction: public_key calulated using Mywallet lib {}'.format(public_key))
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
pkHash10 = keyUtils.pubKeyToAddr(public_key)
print('MyTransaction1: pkHash calulated using KeyUtils lib {}'.format(pkHash10))

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