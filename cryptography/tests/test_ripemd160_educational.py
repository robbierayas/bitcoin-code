"""
Test suite for the educational RIPEMD-160 implementation

Tests ripemd160_educational.py which includes verbose output for learning.
This version performs SHA-256 first (Bitcoin Hash160).
"""

import sys
import os
import io
from contextlib import redirect_stdout

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from ripemd160_educational import myRipeMD160


class TestRIPEMD160Educational(unittest.TestCase):
    """Test educational RIPEMD-160 implementation (Hash160 version)."""

    def test_output_format(self):
        """Test that output is binary bytes (20 bytes)."""
        # Simple compressed public key (33 bytes)
        pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'

        # Run with verbose=False to avoid print output during test
        result = myRipeMD160(pubkey, verbose=False)

        # Should be binary bytes
        self.assertIsInstance(result, bytes, "Output should be bytes")

        # Should be 20 bytes (160 bits)
        self.assertEqual(len(result), 20, "Output should be 20 bytes (160 bits)")

    def test_hex_conversion(self):
        """Test that result can be converted to hex."""
        pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'
        result = myRipeMD160(pubkey, verbose=False)

        # Convert to hex
        hex_result = result.hex()

        # Should be 40 hex characters (20 bytes)
        self.assertEqual(len(hex_result), 40, "Hex output should be 40 characters")

        # Should be valid hex
        try:
            int(hex_result, 16)
        except ValueError:
            self.fail("Result should be valid hexadecimal")

    def test_deterministic(self):
        """Test that same input produces same output."""
        pubkey = '0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352' + \
                 '2cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6'

        result1 = myRipeMD160(pubkey, verbose=False)
        result2 = myRipeMD160(pubkey, verbose=False)
        result3 = myRipeMD160(pubkey, verbose=False)

        self.assertEqual(result1, result2, "Same input should produce same output")
        self.assertEqual(result2, result3, "Same input should produce same output")

    def test_verbose_output(self):
        """Test that verbose mode produces output."""
        pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'

        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            result = myRipeMD160(pubkey, verbose=True)

        output = f.getvalue()

        # Should have printed something
        self.assertGreater(len(output), 0, "Verbose mode should produce output")

        # Check for expected output elements
        self.assertIn('X (16 message words)', output, "Should show message words")
        self.assertIn('h_initial', output, "Should show initial hash values")
        self.assertIn('hnew', output, "Should show final hash values")
        self.assertIn('hex_data', output, "Should show hex data")

    def test_verbose_shows_rounds(self):
        """Test that verbose mode shows last 5 rounds."""
        pubkey = '0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352' + \
                 '2cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6'

        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            result = myRipeMD160(pubkey, verbose=True)

        output = f.getvalue()

        # Should show rounds 4, j 11-15 (last 5 rounds)
        self.assertIn('round 4', output, "Should show round 4")
        self.assertIn('h_left', output, "Should show left line state")
        self.assertIn('h_right', output, "Should show right line state")

    def test_different_pubkeys_different_hashes(self):
        """Test that different public keys produce different hashes."""
        pubkey1 = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'
        pubkey2 = '03ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'

        result1 = myRipeMD160(pubkey1, verbose=False)
        result2 = myRipeMD160(pubkey2, verbose=False)

        self.assertNotEqual(result1, result2,
                           "Different public keys should produce different hashes")

    def test_compressed_pubkey(self):
        """Test with compressed public key (33 bytes, starts with 02 or 03)."""
        # Compressed public key
        pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'

        result = myRipeMD160(pubkey, verbose=False)

        # Should produce 20-byte hash
        self.assertEqual(len(result), 20)

        # Should be valid hex output
        hex_result = result.hex()
        self.assertEqual(len(hex_result), 40)

    def test_uncompressed_pubkey(self):
        """Test with uncompressed public key (65 bytes, starts with 04)."""
        # Uncompressed public key
        pubkey = '0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352' + \
                 '2cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6'

        result = myRipeMD160(pubkey, verbose=False)

        # Should produce 20-byte hash
        self.assertEqual(len(result), 20)

        # Should be valid hex output
        hex_result = result.hex()
        self.assertEqual(len(hex_result), 40)

    def test_quiet_mode(self):
        """Test that verbose=False suppresses output."""
        pubkey = '0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352'

        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            result = myRipeMD160(pubkey, verbose=False)

        output = f.getvalue()

        # Should have no output when verbose=False
        self.assertEqual(len(output), 0, "Quiet mode should produce no output")


class TestRIPEMD160EducationalUtilities(unittest.TestCase):
    """Test utility functions in educational version."""

    def test_compression_function(self):
        """Test that compression function exists and runs."""
        from ripemd160_educational import compression

        # Test with dummy values
        A, B, C, D, E = compression(1, 2, 3, 4, 5, 1, 100, 200, 5)

        # Should return 5 values
        self.assertEqual(len((A, B, C, D, E)), 5)

    def test_cyclic_shift(self):
        """Test cyclic shift function."""
        from ripemd160_educational import cyclicShift

        # Test simple rotation
        result = cyclicShift(1, 1)
        self.assertEqual(result, 2)

        # Test wrapping
        result = cyclicShift(1, 31)
        self.assertEqual(result, 0x80000000)

    def test_little_end(self):
        """Test little-endian conversion."""
        from ripemd160_educational import little_end

        # Test hex conversion
        result = little_end('12345678', 16)
        self.assertEqual(result, '78563412')

        # Test binary conversion
        result = little_end('0000000011111111', 2)
        self.assertEqual(result, '1111111100000000')

    def test_boolean_functions(self):
        """Test that all 5 boolean functions work."""
        from ripemd160_educational import function1, function2, function3, function4, function5

        # Test with sample values
        B, C, D = 0x12345678, 0x9ABCDEF0, 0x11111111

        # All functions should return integers
        self.assertIsInstance(function1(B, C, D), int)
        self.assertIsInstance(function2(B, C, D), int)
        self.assertIsInstance(function3(B, C, D), int)
        self.assertIsInstance(function4(B, C, D), int)
        self.assertIsInstance(function5(B, C, D), int)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestRIPEMD160Educational))
    suite.addTests(loader.loadTestsFromTestCase(TestRIPEMD160EducationalUtilities))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
