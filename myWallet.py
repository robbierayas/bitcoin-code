#This program creates wallet from defined private key
#if no public key, make one
import random
import keyUtils
import sys

def createAddress(private_key):
	
	#	print 'null'
	#	private_key ''.join(['%x' % random.randrange(16) for x in range(0, 64)])
	print 'private key {}'.format(private_key)
	public_key = keyUtils.privateKeyToPublicKey(private_key)
	print 'public key {}'.format(public_key)

	address=keyUtils.keyToAddr(private_key)
	print 'Address {}'.format(address)

	wif=keyUtils.privateKeyToWif(private_key)
	print 'Wif {}'.format(wif)
	
	return public_key
