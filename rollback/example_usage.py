"""
Example usage of the rollback system.

This script demonstrates how to use the refactored rollback system
for RIPEMD-160 and ECDSA rollback operations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback import RollbackRipeMD160, RollbackECDSA, RollbackRunner
from config import TestKeys
from cryptography import keyUtils


def example_basic_ripemd160():
    """Example 1: Basic RIPEMD-160 rollback."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic RIPEMD-160 Rollback")
    print("=" * 70)

    # Generate a Bitcoin address from a test key
    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)
    print(f"Target Address: {address}")

    # Create and run rollback
    rollback = RollbackRipeMD160(address)
    result = rollback.run()

    print("\nResult:")
    print(result)


def example_quiet_ripemd160():
    """Example 2: Quiet RIPEMD-160 rollback (no verbose output)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Quiet RIPEMD-160 Rollback")
    print("=" * 70)

    # Generate a Bitcoin address
    address = keyUtils.keyToAddr(TestKeys.KEY1_HEX)
    print(f"Target Address: {address}")

    # Create rollback with verbose disabled
    rollback = RollbackRipeMD160(address)
    rollback.set_verbose(False)

    result = rollback.run()

    print("\nResult (concise):")
    print(f"Keys found: {len(result.get('X', []))}")


def example_runner_with_config():
    """Example 3: Using the diagnostic runner with configuration."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Diagnostic Runner with Configuration")
    print("=" * 70)

    # Create configuration
    config = {
        'verbose': True,
        'log_to_file': False,  # Set to True to save results
        'output_dir': 'output',
        'show_timing': True,
        'pretty_print': True
    }

    # Create runner
    runner = RollbackRunner(config)

    # Generate test address
    address = keyUtils.keyToAddr(TestKeys.KEY2_HEX)

    # Run RIPEMD-160 rollback with diagnostics
    result = runner.run_ripemd160(address, mechanism_type='brute')

    print(f"\nSuccess: {result.get('success')}")
    print(f"Execution Time: {result.get('execution_time', 0):.4f} seconds")


def example_ecdsa_placeholder():
    """Example 4: ECDSA rollback (placeholder - not yet implemented)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: ECDSA Rollback (Not Yet Implemented)")
    print("=" * 70)

    # Generate a public key
    public_key = keyUtils.privateKeyToPublicKey(TestKeys.KEY1_HEX)
    print(f"Target Public Key: {public_key}")

    try:
        # Attempt ECDSA rollback (will fail with NotImplementedError)
        rollback = RollbackECDSA(public_key)
        result = rollback.run()
    except NotImplementedError as e:
        print(f"\nExpected Error: {e}")
        print("ECDSA rollback mechanism is a placeholder for future implementation.")


def example_backward_compatibility():
    """Example 5: Backward compatibility with old interface."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Backward Compatibility")
    print("=" * 70)

    # Use the old myRollBack function (still works)
    from rollback.rollbackRipeMD160 import myRollBack

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)
    print(f"Target Address: {address}")
    print("\nCalling myRollBack (old interface)...")

    result = myRollBack(address)
    print(f"\nReturned result type: {type(result)}")


if __name__ == '__main__':
    """Run all examples."""
    print("\n" * 2)
    print("#" * 70)
    print("# ROLLBACK SYSTEM EXAMPLES")
    print("#" * 70)

    # Run examples
    try:
        example_basic_ripemd160()
    except Exception as e:
        print(f"Error in example 1: {e}")

    try:
        example_quiet_ripemd160()
    except Exception as e:
        print(f"Error in example 2: {e}")

    try:
        example_runner_with_config()
    except Exception as e:
        print(f"Error in example 3: {e}")

    try:
        example_ecdsa_placeholder()
    except Exception as e:
        print(f"Error in example 4: {e}")

    try:
        example_backward_compatibility()
    except Exception as e:
        print(f"Error in example 5: {e}")

    print("\n" + "#" * 70)
    print("# EXAMPLES COMPLETE")
    print("#" * 70)
    print("\n")
