#creates address
import myWallet
import myCrypto

import utils
import keyUtils

import math
import hashlib

#public_key=myWallet.createAddress('4eb2eeac47c1dbba95a97cf32fd25a22410195bb64b64ba5f0fa6e0896ba31ca')
print ''
print 'MyTransaction: private key a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f'
print ''
print ''
print ''
print 'Method 1'
public_key=myWallet.createAddress('a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f')
print 'MyTransaction: public_key calulated using Mywallet lib {}'.format(public_key)

pkHash=keyUtils.pubKeyToAddr(public_key)
print 'MyTransaction: pkHash calulated using KeyUtils lib {}'.format(pkHash)
print ''
print ''
print ''
print 'Method 2'
pkHashStep1=hashlib.sha256(public_key.decode('hex')).digest()
print 'MyTransaction: pkHashStep1 calculated from sha256(publickey) {}'.format(pkHashStep1)
print 'MyTransaction: pkHashStep1 calculated from sha256(publickey) {}'.format(pkHashStep1.encode('hex'))
print 'pkHashStep1 type {}'.format(type(pkHashStep1))

ripemd160=hashlib.new('ripemd160')
ripemd160.update(pkHashStep1)
ripemd160digest=ripemd160.digest()
print 'ripemd160digest {}'.format(ripemd160digest)
print 'ripemd160digest {}'.format(ripemd160digest.encode('hex'))
pkHashStep2=utils.base58CheckEncode(0, ripemd160digest) 
print 'MyTransaction pkHashStep2 calculated from ripemd160 hashlib base58(RIPEMD160(SHA256(PK))) {}'.format(pkHashStep2)

print ''
print ''
print ''
print 'Method 3'
pkHashStep21=myCrypto.myRipeMD160(public_key)
print 'MyTransaction pkHashStep2 {}'.format(pkHashStep21)
print 'MyTransaction pkHashStep2 {}'.format(pkHashStep21.decode('hex'))
pkHashStep22=utils.base58CheckEncode(0, pkHashStep21) 



print 'MyTransaction pkHashStep2 calculated from ripemd160 func base58(RIPEMD160(SHA256(PK))) {}'.format(pkHashStep22)


