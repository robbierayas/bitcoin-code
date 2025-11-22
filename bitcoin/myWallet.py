#This program creates wallet from defined private key
#if no public key, make one
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import random
from cryptography import keyUtils

def createAddress(private_key):
	
	#	print 'null'
	#	private_key ''.join(['%x' % random.randrange(16) for x in range(0, 64)])
	public_key = keyUtils.privateKeyToPublicKey(private_key)
	address=keyUtils.keyToAddr(private_key)
	wif=keyUtils.privateKeyToWif(private_key)	
	return public_key
