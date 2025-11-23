#!/usr/bin/env python
"""
Simple command-line interface for rollback operations.

This provides an easy-to-use CLI for running rollback operations with
configuration from config.py.

Usage:
    python rollback/run.py                           # Interactive mode
    python rollback/run.py key1                      # Use test address
    python rollback/run.py <address>                 # Custom address
    python rollback/run.py --list-tests              # List test addresses
    python rollback/run.py --compare                 # Compare methods
    python rollback/run.py --performance             # Run performance tests
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
from rollback import RollbackRipeMD160, RollbackECDSA, RollbackRunner, PerformanceTracker
from config import RollbackConfig, TestKeys
from cryptography import keyUtils


def list_test_addresses():
    """List available test addresses."""
    print("\n" + "=" * 70)
    print("AVAILABLE TEST ADDRESSES")
    print("=" * 70)
    print("\nFrom RollbackConfig.TEST_ADDRESSES:")
    for name, address in RollbackConfig.TEST_ADDRESSES.items():
        print(f"  {name}: {address}")

    print("\nGenerate from TestKeys:")
    print(f"  KEY1: {keyUtils.keyToAddr(TestKeys.KEY1_HEX)}")
    print(f"  KEY2: {keyUtils.keyToAddr(TestKeys.KEY2_HEX)}")
    print(f"  KEY3: {keyUtils.keyToAddr(TestKeys.KEY3_HEX)}")
    print("\nUsage: python rollback/run.py key1")
    print("=" * 70)


def run_simple_ecdsa(target, max_iterations=None, progress_interval=1000):
    """Run a simple ECDSA rollback with default config."""
    print("\n" + "=" * 70)
    print("SIMPLE ECDSA ROLLBACK MODE (PLACEHOLDER)")
    print("=" * 70)
    print(f"Target: {target[:50]}..." if len(str(target)) > 50 else f"Target: {target}")
    print("Using config from: config.py (RollbackConfig)")
    if max_iterations:
        print(f"Max Iterations: {max_iterations:,}")
    else:
        print(f"Max Iterations: 100 (placeholder default)")
    print(f"Progress Interval: {progress_interval:,}")
    print("-" * 70)

    # Use default config from config.py
    rollback = RollbackECDSA(
        target,
        max_iterations=max_iterations or 100,  # Default to 100 for placeholder
        progress_interval=progress_interval
    )
    result = rollback.run()

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    if result:
        print(f"Found: {result.get('found', False)}")
        stats = result.get('stats', {})
        if stats:
            print(f"Iterations: {stats.get('total_iterations', 0):,}")
            print(f"Keys tested: {stats.get('keys_tested', 0):,}")
            if stats.get('stopped_early'):
                print(f"Stopped early: {stats.get('stop_reason')}")
        print(f"\nNote: {result.get('note', 'N/A')}")
    else:
        print("No results returned")


def run_simple_rollback(address, max_iterations=None, progress_interval=1000):
    """Run a simple rollback with default config."""
    print("\n" + "=" * 70)
    print("SIMPLE ROLLBACK MODE")
    print("=" * 70)
    print(f"Address: {address}")
    print("Using config from: config.py (RollbackConfig)")
    if max_iterations:
        print(f"Max Iterations: {max_iterations:,}")
    print(f"Progress Interval: {progress_interval:,}")
    print("-" * 70)

    # Use default config from config.py
    rollback = RollbackRipeMD160(
        address,
        max_iterations=max_iterations,
        progress_interval=progress_interval
    )
    result = rollback.run()

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    if result:
        x_values = result.get('X', [])
        non_empty = [x for x in x_values if x != '']
        print(f"Found {len(non_empty)} non-empty X values")
        print(f"Total X array length: {len(x_values)}")
    else:
        print("No results returned")


def run_with_runner(address, max_iterations=None, progress_interval=1000):
    """Run rollback using RollbackRunner."""
    print("\n" + "=" * 70)
    print("RUNNER MODE")
    print("=" * 70)
    print(f"Address: {address}")
    print("Using RollbackRunner with config.py defaults")
    if max_iterations:
        print(f"Max Iterations: {max_iterations:,}")
    print(f"Progress Interval: {progress_interval:,}")
    print("-" * 70)

    # Uses RollbackConfig.RUNNER_CONFIG automatically
    runner = RollbackRunner()
    # Note: runner doesn't support max_iterations yet, so we'll just run it normally
    result = runner.run_ripemd160(address)

    return result


def run_quiet(address, max_iterations=None, progress_interval=1000):
    """Run rollback in quiet mode."""
    info_msg = f"\nRunning rollback for {address} (quiet mode)"
    if max_iterations:
        info_msg += f" - max {max_iterations:,} iterations"
    print(info_msg + "...")

    rollback = RollbackRipeMD160(
        address,
        max_iterations=max_iterations,
        progress_interval=progress_interval
    )
    rollback.set_verbose(False)
    result = rollback.run()

    if result:
        x_values = result.get('X', [])
        non_empty = [x for x in x_values if x != '']
        stats = result.get('stats', {})
        print(f"[OK] Complete. Found {len(non_empty)} values.")
        if stats:
            print(f"  Iterations: {stats.get('total_iterations', 0):,}")
            print(f"  Brute force attempts: {stats.get('brute_force_attempts', 0):,}")
            if stats.get('stopped_early'):
                print(f"  Stopped early: {stats.get('stop_reason')}")

    return result


def run_comparison():
    """Compare different rollback methods."""
    print("\n" + "=" * 70)
    print("METHOD COMPARISON MODE")
    print("=" * 70)

    # Get test address
    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)
    print(f"Test Address: {address}")
    print("Comparing 3 different methods...")
    print("-" * 70)

    # Configure performance tracker
    config = RollbackConfig.PERFORMANCE_CONFIG.copy()
    config['repeat_runs'] = 2  # Run each test twice
    config['print_summary'] = False  # Don't print individual summaries

    tracker = PerformanceTracker(config)

    # Method 1: Direct rollback
    def method1():
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(False)
        return rollback.run()

    # Method 2: Using runner
    def method2():
        runner = RollbackRunner()
        # Override verbose to quiet
        runner.verbose = False
        return runner.run_ripemd160(address)

    # Method 3: Rollback with mechanism specified
    def method3():
        rollback = RollbackRipeMD160(address, mechanism_type='brute')
        rollback.set_verbose(False)
        return rollback.run()

    # Track each method
    print("\n[1/3] Testing Direct Rollback...")
    tracker.track('Direct Rollback', method1)

    print("\n[2/3] Testing Via Runner...")
    tracker.track('Via Runner', method2)

    print("\n[3/3] Testing With Mechanism Type...")
    tracker.track('With Mechanism Type', method3)

    # Show comparison
    print("\n")
    tracker.print_comparison()

    # Save results
    tracker.save_results('method_comparison.json')

    return tracker


def run_performance_tests():
    """Run performance tests on different addresses."""
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST MODE")
    print("=" * 70)
    print("Testing rollback performance on 3 different addresses")
    print("-" * 70)

    # Get test addresses
    addresses = {
        'KEY1': keyUtils.keyToAddr(TestKeys.KEY1_HEX),
        'KEY2': keyUtils.keyToAddr(TestKeys.KEY2_HEX),
        'KEY3': keyUtils.keyToAddr(TestKeys.KEY3_HEX),
    }

    # Configure tracker
    config = RollbackConfig.PERFORMANCE_CONFIG.copy()
    config['repeat_runs'] = 1
    config['print_summary'] = True

    tracker = PerformanceTracker(config)

    # Test each address
    for i, (name, address) in enumerate(addresses.items(), 1):
        print(f"\n[{i}/3] Testing {name}: {address[:20]}...")

        def run_test():
            rollback = RollbackRipeMD160(address)
            rollback.set_verbose(False)
            return rollback.run()

        tracker.track(f'Address_{name}', run_test)

    # Show comparison
    print("\n")
    tracker.print_comparison()

    # Save results
    tracker.save_results('address_performance.json')

    return tracker


def interactive_mode():
    """Interactive mode - prompt user for input."""
    print("\n" + "=" * 70)
    print("ROLLBACK INTERACTIVE MODE")
    print("=" * 70)

    print("\nOptions:")
    print("  1. Use a test address (key1, key2, key3)")
    print("  2. Enter a custom Bitcoin address")
    print("  3. Compare different methods")
    print("  4. Run performance tests")
    print("  5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == '1':
        print("\nAvailable test addresses:")
        for name in RollbackConfig.TEST_ADDRESSES.keys():
            print(f"  - {name}")
        key = input("\nEnter test key name: ").strip()

        if key in RollbackConfig.TEST_ADDRESSES:
            address = RollbackConfig.TEST_ADDRESSES[key]
            run_simple_rollback(address)
        else:
            print(f"Unknown test key: {key}")

    elif choice == '2':
        address = input("\nEnter Bitcoin address: ").strip()
        run_simple_rollback(address)

    elif choice == '3':
        run_comparison()

    elif choice == '4':
        run_performance_tests()

    elif choice == '5':
        print("\nExiting...")
        sys.exit(0)

    else:
        print(f"\nInvalid choice: {choice}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Rollback CLI - Easy command-line interface for rollback operations',
        epilog="""
Examples:
  # General
  python rollback/run.py                               # Interactive mode
  python rollback/run.py --list-tests                  # List test addresses
  python rollback/run.py --compare                     # Compare methods
  python rollback/run.py --performance                 # Run performance tests

  # RIPEMD-160 rollback (default)
  python rollback/run.py key1                          # Use test address key1
  python rollback/run.py 1A1zP1e...                    # Use custom address
  python rollback/run.py key3 --quiet                  # Quiet mode
  python rollback/run.py key3 --max-iterations 5000    # Limit iterations

  # ECDSA rollback (placeholder)
  python rollback/run.py key1 --type ecdsa             # ECDSA with test key
  python rollback/run.py 04abc... --type ecdsa         # ECDSA with pubkey
  python rollback/run.py key3 --type ecdsa --quiet     # ECDSA quiet mode
  python rollback/run.py key2 --type ecdsa --max-iterations 1000
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'target',
        nargs='?',
        help='Target: Bitcoin address for RIPEMD-160 or public key for ECDSA (or test key name: key1, key2, key3)'
    )
    parser.add_argument(
        '--type',
        choices=['ripemd160', 'ecdsa'],
        default='ripemd160',
        help='Type of rollback: ripemd160 (default) or ecdsa'
    )
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List available test addresses'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare different rollback methods'
    )
    parser.add_argument(
        '--performance',
        action='store_true',
        help='Run performance tests on multiple addresses'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Run in quiet mode (minimal output)'
    )
    parser.add_argument(
        '--runner',
        action='store_true',
        help='Use RollbackRunner instead of direct rollback'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        metavar='N',
        help='Stop after N iterations (useful for testing performance)'
    )
    parser.add_argument(
        '--progress-interval',
        type=int,
        default=1000,
        metavar='N',
        help='Report progress every N iterations (default: 1000)'
    )

    args = parser.parse_args()

    # Handle special modes
    if args.list_tests:
        list_test_addresses()
        return

    if args.compare:
        run_comparison()
        return

    if args.performance:
        run_performance_tests()
        return

    # If no target provided, use interactive mode
    if not args.target:
        interactive_mode()
        return

    # Check if it's a test key name and convert to address/pubkey
    target = args.target
    rollback_type = args.type

    if target.lower() in ['key1', 'key2', 'key3']:
        # Also support KEY1, KEY2, KEY3 format
        key_map = {
            'key1': TestKeys.KEY1_HEX,
            'key2': TestKeys.KEY2_HEX,
            'key3': TestKeys.KEY3_HEX,
        }

        if rollback_type == 'ripemd160':
            print(f"\nGenerating address from {target.upper()}...")
            target = keyUtils.keyToAddr(key_map[target.lower()])
        elif rollback_type == 'ecdsa':
            print(f"\nGenerating public key from {target.upper()}...")
            target = keyUtils.privateKeyToPublicKey(key_map[target.lower()])
    elif target in RollbackConfig.TEST_ADDRESSES:
        # For RIPEMD160 only
        if rollback_type == 'ripemd160':
            print(f"\nUsing test address for '{target}'")
            target = RollbackConfig.TEST_ADDRESSES[target]

    # Run rollback
    max_iterations = getattr(args, 'max_iterations', None)
    progress_interval = getattr(args, 'progress_interval', 1000)

    if rollback_type == 'ecdsa':
        # ECDSA rollback
        if args.quiet:
            print(f"\nRunning ECDSA rollback for {target[:50]}... (quiet mode)")
            rollback = RollbackECDSA(target, max_iterations=max_iterations or 100, progress_interval=progress_interval)
            rollback.set_verbose(False)
            result = rollback.run()
            if result:
                print(f"[OK] Complete. Found: {result.get('found', False)}")
                stats = result.get('stats', {})
                if stats:
                    print(f"  Iterations: {stats.get('total_iterations', 0):,}")
        else:
            run_simple_ecdsa(target, max_iterations, progress_interval)
    else:
        # RIPEMD-160 rollback (default)
        if args.quiet:
            run_quiet(target, max_iterations, progress_interval)
        elif args.runner:
            run_with_runner(target, max_iterations, progress_interval)
        else:
            run_simple_rollback(target, max_iterations, progress_interval)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
