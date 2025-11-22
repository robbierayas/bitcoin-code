import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import random, keyUtils

private_key = ''.join(['%x' % random.randrange(16) for x in range(0, 64)])
print keyUtils.privateKeyToWif(private_key)
print keyUtils.keyToAddr(private_key)

