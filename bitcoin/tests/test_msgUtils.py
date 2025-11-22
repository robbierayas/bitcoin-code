"""
Test suite for Bitcoin message utilities

Tests msgUtils.py which handles:
- Bitcoin P2P protocol message creation and parsing
- Version messages
- Inventory messages
- Address messages
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import struct

from bitcoin import msgUtils


class TestMsgUtils(unittest.TestCase):
    """Test Bitcoin message utility functions."""

    def test_processVersion(self):
        """Test parsing Bitcoin version message."""
        header = (b'\xf9\xbe\xb4\xd9\x76\x65\x72\x73\x69\x6f\x6e\x00\x00\x00\x00\x00' +
                  b'\x66\x00\x00\x00\x85\xe6\xaa\x94')
        payload = (b'\x71\x11\x01\x00\x01\x00\x00\x00' +
                   b'\x00\x00\x00\x00\xa2\x31\xa0\x52\x00\x00\x00\x00\x01\x00\x00\x00' +
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff' +
                   b'\x6c\x51\xe0\xee\xd8\x73\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x62\x91\x98\x16\x20\x8d' +
                   b'\xf4\x7d\x37\xbf\xe4\xe7\x1f\xd2\x11\x2f\x53\x61\x74\x6f\x73\x68' +
                   b'\x69\x3a\x30\x2e\x38\x2e\x32\x2e\x32\x2f\x02\x2b\x04\x00')

        # Verify message parses without errors
        result = msgUtils.processChunk(header, payload)

        # Version messages return None (they just print)
        self.assertIsNone(result)

    def test_processInv(self):
        """Test parsing Bitcoin inventory message."""
        header = (b'\xf9\xbe\xb4\xd9\x69\x6e\x76\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                  b'\x25\x00\x00\x00\x73\x3b\xf4\x95')
        payload = (b'\x01\x01\x00\x00\x00\xd4\xe5\xc2' +
                   b'\x8b\x09\x45\x05\xce\xec\x7c\x61\x34\xd1\xbd\x16\x80\x69\xc8\xc9' +
                   b'\xc3\x31\x93\xb5\x87\x27\xd9\xda\x7d\xa2\x80\x23\x20')

        chunks = msgUtils.processChunk(header, payload)

        # Should return list of inventory items
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0][0], 1)  # MSG_TX type
        self.assertEqual(chunks[0][1], (b'\xd4\xe5\xc2\x8b\x09\x45\x05\xce\xec\x7c\x61\x34\xd1\xbd\x16\x80' +
                                        b'\x69\xc8\xc9\xc3\x31\x93\xb5\x87\x27\xd9\xda\x7d\xa2\x80\x23\x20'))


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMsgUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
