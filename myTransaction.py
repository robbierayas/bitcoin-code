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
public_key=myWallet.createAddress('a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f')
#public_key=''
print 'MyTransaction: public_key calulated using Mywallet lib {}'.format(public_key)
print 'public_key type {}'.format(type(public_key))


print ''
print ''
print ''
print 'C library'
from Crypto.Hash import RIPEMD160
hash = RIPEMD160.new()
pkHashStep00=hashlib.sha256(public_key.decode('hex')).digest()
hash.update(pkHashStep00)
cdigest=hash.digest()
print 'MyTransaction0: pkHashStep00 calculated from clib(publickey) {}'.format(cdigest.encode('hex'))
pkHashStep01=utils.base58CheckEncode(0, cdigest) 
print 'MyTransaction0: pkHash calculated from clib(publickey) {}'.format(pkHashStep01)
print ''
print 'C library step by step'

print ''
print ''
print ''
print 'Method 1'
pkHash10=keyUtils.pubKeyToAddr(public_key)
print 'MyTransaction1: pkHash calulated using KeyUtils lib {}'.format(pkHash10)

print ''
print ''
print ''
print 'Method 2'
pkHashStep20=hashlib.sha256(public_key.decode('hex')).digest()
#print 'MyTransaction2: pkHashStep20 calculated from sha256(publickey) {}'.format(pkHashStep20)
print 'MyTransaction2: pkHashStep20 calculated from sha256(publickey) {}'.format(pkHashStep20.encode('hex'))
#print 'pkHashStep20 type {}'.format(type(pkHashStep20))
ripemd1602=hashlib.new('ripemd160')
ripemd1602.update(pkHashStep20)
ripemd160digest=ripemd1602.digest()
print 'MyTransaction2: ripemd160digest {}'.format(ripemd160digest)
print 'MyTransaction2: ripemd160digest {}'.format(ripemd160digest.encode('hex'))
pkHashStep21=utils.base58CheckEncode(0, ripemd160digest) 
print 'MyTransaction2: pkHash calculated from ripemd160 hashlib base58(RIPEMD160(SHA256(PK))) {}'.format(pkHashStep21)

print ''
print ''
print ''
print 'Method 3'
pkHashStep30=myCrypto.myRipeMD160(public_key)
print 'MyTransaction 3: pkHashStep30 {}'.format(pkHashStep30)
pkHashStep31=utils.base58CheckEncode(0,pkHashStep30) 


print 'MyTransaction 3:pkHashStep31 calculated from ripemd160 func base58(RIPEMD160(SHA256(PK))) {}'.format(pkHashStep31)

