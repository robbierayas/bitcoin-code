#creates address
import myWallet
import myCrypto

import utils
import keyUtils

import math
import hashlib

#public_key=myWallet.createAddress('4eb2eeac47c1dbba95a97cf32fd25a22410195bb64b64ba5f0fa6e0896ba31ca')
public_key=myWallet.createAddress('a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f')
print 'MyTransaction public_key {}'.format(public_key)

pkHash=keyUtils.pubKeyToAddr(public_key)
print 'MyTransaction pkHash {}'.format(pkHash)

#pkHashStep1=hashlib.sha256(public_key.decode('hex')).digest()
pkHashStep1=hashlib.sha256(public_key.decode('hex')).digest()
print 'MyTransaction pkHashStep1 {}'.format(pkHashStep1)
print 'pkHashStep1 {}'.format(type(pkHashStep1))

ripemd160=hashlib.new('ripemd160')
ripemd160.update(pkHashStep1)
pkHashStep2=utils.base58CheckEncode(0, ripemd160.digest()) 
print 'MyTransaction pkHashStep2 {}'.format(pkHashStep2)




pkHashStep21=hashlib.sha256(public_key.decode('hex')).digest()
print 'MyTransaction pkHashStep1 {}'.format(pkHashStep21)
print len(pkHashStep21)
print 'pkHashStep1 {}'.format(type(pkHashStep21))


#pkHashStep22=myCrypto.myRipeMD160(pkHashStep21)
pkHashStep22=myCrypto.myRipeMD160(public_key)

print 'MyTransaction pkHashStep2 {}'.format(pkHashStep22)


