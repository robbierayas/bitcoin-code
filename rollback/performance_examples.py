"""
Performance Tracking Examples for Rollback Mechanisms.

This module demonstrates best practices for tracking and comparing
performance of different rollback methods and implementations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rollback.performance import (
    timing_decorator,
    detailed_timing_decorator,
    timer,
    memory_tracker,
    PerformanceTracker,
    compare_methods
)
from rollback import RollbackRipeMD160, RollbackRunner
from config import TestKeys, RollbackConfig
from cryptography import keyUtils


# ============================================================================
# EXAMPLE 1: Simple Timing Decorator
# ============================================================================

@timing_decorator
def example1_simple_timing():
    """Example 1: Using simple timing decorator."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Timing Decorator")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)
    rollback = RollbackRipeMD160(address)
    rollback.set_verbose(False)  # Quiet mode for cleaner output
    result = rollback.run()

    print(f"Result keys found: {len([x for x in result.get('X', []) if x != ''])}")


# ============================================================================
# EXAMPLE 2: Detailed Timing Decorator
# ============================================================================

@detailed_timing_decorator(name="RIPEMD-160 Rollback", enabled=True)
def example2_detailed_timing():
    """Example 2: Using detailed timing decorator with CPU/Wall time."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Detailed Timing Decorator")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)
    rollback = RollbackRipeMD160(address)
    rollback.set_verbose(False)
    result = rollback.run()

    print(f"Result keys found: {len([x for x in result.get('X', []) if x != ''])}")


# ============================================================================
# EXAMPLE 3: Context Manager for Timing Blocks
# ============================================================================

def example3_context_manager():
    """Example 3: Using context manager to time specific blocks."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Context Manager for Timing")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)

    # Time the initialization
    with timer("Rollback Initialization"):
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(False)

    # Time the actual rollback
    timing_info = {}
    with timer("Rollback Execution", verbose=True) as timing_info:
        result = rollback.run()

    print(f"\nResult keys found: {len([x for x in result.get('X', []) if x != ''])}")
    print(f"Execution took: {timing_info.get('wall_time', 0):.6f} seconds")


# ============================================================================
# EXAMPLE 4: Memory Tracking
# ============================================================================

def example4_memory_tracking():
    """Example 4: Track memory usage during rollback."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Memory Tracking")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)

    with memory_tracker("RIPEMD-160 Rollback", verbose=True):
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(False)
        result = rollback.run()

    print(f"\nResult keys found: {len([x for x in result.get('X', []) if x != ''])}")


# ============================================================================
# EXAMPLE 5: Performance Tracker - Single Method
# ============================================================================

def example5_performance_tracker():
    """Example 5: Using PerformanceTracker for detailed analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: PerformanceTracker with Multiple Runs")
    print("=" * 70)

    # Configure for multiple runs
    config = RollbackConfig.PERFORMANCE_CONFIG.copy()
    config['warmup_runs'] = 0  # No warmup needed for this example
    config['repeat_runs'] = 3  # Run 3 times for statistics

    tracker = PerformanceTracker(config)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)

    def run_rollback():
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(False)
        return rollback.run()

    # Track the method
    result = tracker.track('RIPEMD160_Rollback', run_rollback)

    # Get statistics
    stats = tracker.get_statistics('RIPEMD160_Rollback')
    print(f"\nStatistics:")
    print(f"  Mean time: {stats.get('wall_time_mean', 0):.6f}s")
    print(f"  Min time:  {stats.get('wall_time_min', 0):.6f}s")
    print(f"  Max time:  {stats.get('wall_time_max', 0):.6f}s")
    if 'wall_time_stdev' in stats:
        print(f"  StdDev:    {stats.get('wall_time_stdev', 0):.6f}s")

    # Save results
    tracker.save_results('example5_results.json')


# ============================================================================
# EXAMPLE 6: Comparing Multiple Methods
# ============================================================================

def example6_compare_methods():
    """Example 6: Compare different rollback implementations."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comparing Multiple Methods")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)

    # Define methods to compare
    def method_verbose():
        """Rollback with verbose output."""
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(True)
        return rollback.run()

    def method_quiet():
        """Rollback with quiet output."""
        rollback = RollbackRipeMD160(address)
        rollback.set_verbose(False)
        return rollback.run()

    def method_runner():
        """Rollback using RollbackRunner."""
        runner = RollbackRunner()
        return runner.run_ripemd160(address)

    # Configure tracker
    config = RollbackConfig.PERFORMANCE_CONFIG.copy()
    config['warmup_runs'] = 0
    config['repeat_runs'] = 2
    config['print_summary'] = False  # We'll print comparison instead

    tracker = PerformanceTracker(config)

    # Track each method
    print("\nRunning method 1: Verbose output...")
    tracker.track('Verbose Output', method_verbose)

    print("\nRunning method 2: Quiet output...")
    tracker.track('Quiet Output', method_quiet)

    print("\nRunning method 3: Using Runner...")
    tracker.track('Using Runner', method_runner)

    # Print comparison
    tracker.print_comparison()

    # Save results
    tracker.save_results('example6_comparison.json')


# ============================================================================
# EXAMPLE 7: Using compare_methods Convenience Function
# ============================================================================

def example7_convenience_function():
    """Example 7: Using compare_methods convenience function."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Convenience Function for Quick Comparisons")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY2_HEX)

    # Define methods to compare
    methods = {
        'Direct Rollback': lambda: RollbackRipeMD160(address, 'brute').run(),
        'Via Runner': lambda: RollbackRunner().run_ripemd160(address),
    }

    # Configure
    config = {
        'warmup_runs': 0,
        'repeat_runs': 2,
        'save_results': True,
        'results_dir': 'output/performance'
    }

    # Compare
    tracker = compare_methods(methods, config)
    tracker.save_results('example7_quick_comparison.json')


# ============================================================================
# EXAMPLE 8: Advanced - Profiling Different Addresses
# ============================================================================

def example8_profile_different_addresses():
    """Example 8: Compare performance across different test addresses."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Profiling Different Addresses")
    print("=" * 70)

    config = {
        'warmup_runs': 0,
        'repeat_runs': 1,
        'print_summary': True,
        'save_results': True,
    }

    tracker = PerformanceTracker(config)

    # Test with different addresses
    test_cases = {
        'KEY1': keyUtils.keyToAddr(TestKeys.KEY1_HEX),
        'KEY2': keyUtils.keyToAddr(TestKeys.KEY2_HEX),
        'KEY3': keyUtils.keyToAddr(TestKeys.KEY3_HEX),
    }

    for name, address in test_cases.items():
        print(f"\nTesting {name}: {address}")

        def run_test():
            rollback = RollbackRipeMD160(address)
            rollback.set_verbose(False)
            return rollback.run()

        tracker.track(f'Address_{name}', run_test)

    # Compare
    tracker.print_comparison()
    tracker.save_results('example8_address_comparison.json')


# ============================================================================
# EXAMPLE 9: Combining Timer and Memory Tracker
# ============================================================================

def example9_combined_tracking():
    """Example 9: Combine time and memory tracking."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Combined Time and Memory Tracking")
    print("=" * 70)

    address = keyUtils.keyToAddr(TestKeys.KEY3_HEX)

    # Nested context managers
    with timer("Complete Operation"):
        with memory_tracker("Memory Usage"):
            rollback = RollbackRipeMD160(address)
            rollback.set_verbose(False)
            result = rollback.run()

    print(f"\nResult keys found: {len([x for x in result.get('X', []) if x != ''])}")


# ============================================================================
# MAIN - Run All Examples
# ============================================================================

if __name__ == '__main__':
    """Run all performance tracking examples."""

    print("\n" * 2)
    print("#" * 70)
    print("# PERFORMANCE TRACKING EXAMPLES")
    print("#" * 70)

    examples = [
        ("Simple Timing", example1_simple_timing),
        ("Detailed Timing", example2_detailed_timing),
        ("Context Manager", example3_context_manager),
        ("Memory Tracking", example4_memory_tracking),
        ("Performance Tracker", example5_performance_tracker),
        ("Compare Methods", example6_compare_methods),
        ("Convenience Function", example7_convenience_function),
        ("Profile Addresses", example8_profile_different_addresses),
        ("Combined Tracking", example9_combined_tracking),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n\nRunning Example {i}: {name}")
            example_func()
        except Exception as e:
            print(f"\nError in Example {i}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" * 2)
    print("#" * 70)
    print("# EXAMPLES COMPLETE")
    print("#" * 70)
    print("\nCheck output/performance/ for saved results")
    print("\n")
