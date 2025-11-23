"""
Performance Tracking Utilities for Rollback Mechanisms.

This module provides best-practice performance tracking tools including:
- Decorators for timing and profiling functions
- Context managers for timing code blocks
- PerformanceTracker class for comparing multiple methods
- Memory and CPU profiling utilities
- Visualization and reporting

Best Practices Implemented:
1. Decorator pattern for non-intrusive performance tracking
2. Context managers for clean resource management
3. Centralized metrics collection and comparison
4. Configurable warmup and repeat runs
5. Statistical analysis (min, max, avg, median, stddev)
6. JSON export for further analysis
7. Comparison tables and visualizations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import functools
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Callable, Dict, List, Any, Optional
from statistics import mean, median, stdev
from config import RollbackConfig


# ============================================================================
# TIMING DECORATOR
# ============================================================================

def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Usage:
        @timing_decorator
        def my_function():
            # ... code ...

    Returns:
        Wrapped function that prints execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        print(f"\n[TIMING] {func.__name__}:")
        print(f"  Execution Time: {execution_time:.6f} seconds")

        return result
    return wrapper


def detailed_timing_decorator(name: Optional[str] = None, enabled: bool = True) -> Callable:
    """
    Advanced timing decorator with configurable options.

    Args:
        name: Custom name for the operation (default: function name)
        enabled: Whether timing is enabled (default: True)

    Usage:
        @detailed_timing_decorator(name="My Operation", enabled=True)
        def my_function():
            # ... code ...

    Returns:
        Wrapped function with detailed timing information
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled:
                return func(*args, **kwargs)

            operation_name = name or func.__name__

            # CPU time (process time)
            start_cpu = time.process_time()
            # Wall clock time
            start_wall = time.perf_counter()

            result = func(*args, **kwargs)

            end_cpu = time.process_time()
            end_wall = time.perf_counter()

            cpu_time = end_cpu - start_cpu
            wall_time = end_wall - start_wall

            print(f"\n[DETAILED TIMING] {operation_name}:")
            print(f"  Wall Time: {wall_time:.6f} seconds")
            print(f"  CPU Time:  {cpu_time:.6f} seconds")
            print(f"  Ratio:     {cpu_time/wall_time:.2%} (CPU/Wall)")

            return result
        return wrapper
    return decorator


# ============================================================================
# CONTEXT MANAGER FOR TIMING BLOCKS
# ============================================================================

@contextmanager
def timer(name: str = "Operation", verbose: bool = True):
    """
    Context manager for timing code blocks.

    Usage:
        with timer("My Operation"):
            # ... code to time ...

    Args:
        name: Name of the operation being timed
        verbose: Whether to print timing info

    Yields:
        Dictionary containing timing information
    """
    timing_info = {}

    start_cpu = time.process_time()
    start_wall = time.perf_counter()

    try:
        yield timing_info
    finally:
        end_cpu = time.process_time()
        end_wall = time.perf_counter()

        cpu_time = end_cpu - start_cpu
        wall_time = end_wall - start_wall

        timing_info['name'] = name
        timing_info['wall_time'] = wall_time
        timing_info['cpu_time'] = cpu_time
        timing_info['timestamp'] = datetime.now().isoformat()

        if verbose:
            print(f"\n[TIMER] {name}:")
            print(f"  Wall Time: {wall_time:.6f} seconds")
            print(f"  CPU Time:  {cpu_time:.6f} seconds")


# ============================================================================
# PERFORMANCE TRACKER CLASS
# ============================================================================

class PerformanceTracker:
    """
    Centralized performance tracking and comparison system.

    Tracks multiple methods/implementations and provides detailed comparison
    with statistical analysis.

    Best Practices:
    - Warmup runs to stabilize caching effects
    - Multiple repeat runs for statistical significance
    - Track both wall time and CPU time
    - Optional memory profiling
    - Export results for further analysis
    - Generate comparison tables

    Usage:
        tracker = PerformanceTracker()

        # Run and track method 1
        tracker.track('method1', lambda: method1())

        # Run and track method 2
        tracker.track('method2', lambda: method2())

        # Compare results
        tracker.print_comparison()
        tracker.save_results('results.json')
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the performance tracker.

        Args:
            config: Configuration dict. If None, uses RollbackConfig.PERFORMANCE_CONFIG
        """
        self.config = config if config is not None else RollbackConfig.PERFORMANCE_CONFIG.copy()

        self.results: Dict[str, List[Dict]] = {}
        self.metadata: Dict[str, Any] = {}

        # Create results directory if needed
        if self.config.get('save_results', True):
            results_dir = self.config.get('results_dir', 'output/performance')
            os.makedirs(results_dir, exist_ok=True)

    def track(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """
        Track performance of a function.

        Args:
            name: Name for this method/implementation
            func: Function to track
            *args: Arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            Result of the function call
        """
        if name not in self.results:
            self.results[name] = []

        # Warmup runs
        warmup_runs = self.config.get('warmup_runs', 0)
        for _ in range(warmup_runs):
            func(*args, **kwargs)

        # Actual timed runs
        repeat_runs = self.config.get('repeat_runs', 1)
        result = None

        for run in range(repeat_runs):
            # Measure time
            start_cpu = time.process_time()
            start_wall = time.perf_counter()

            result = func(*args, **kwargs)

            end_cpu = time.process_time()
            end_wall = time.perf_counter()

            # Store results
            run_data = {
                'run': run + 1,
                'wall_time': end_wall - start_wall,
                'cpu_time': end_cpu - start_cpu,
                'timestamp': datetime.now().isoformat()
            }

            # Optional memory tracking
            if self.config.get('track_memory', False):
                try:
                    import psutil
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    run_data['memory_rss'] = memory_info.rss
                    run_data['memory_vms'] = memory_info.vms
                except ImportError:
                    pass

            self.results[name].append(run_data)

        # Print summary if configured
        if self.config.get('print_summary', True):
            self._print_summary(name)

        return result

    def _print_summary(self, name: str):
        """Print summary for a single tracked method."""
        runs = self.results[name]
        if not runs:
            return

        wall_times = [r['wall_time'] for r in runs]
        cpu_times = [r['cpu_time'] for r in runs]

        print(f"\n[PERFORMANCE] {name}:")
        print(f"  Runs: {len(runs)}")
        print(f"  Wall Time: {mean(wall_times):.6f}s (avg) | "
              f"{min(wall_times):.6f}s (min) | "
              f"{max(wall_times):.6f}s (max)")
        if len(wall_times) > 1:
            print(f"  StdDev: {stdev(wall_times):.6f}s")

    def get_statistics(self, name: str) -> Dict[str, float]:
        """
        Get statistical summary for a tracked method.

        Args:
            name: Name of the method

        Returns:
            Dictionary with statistics
        """
        if name not in self.results or not self.results[name]:
            return {}

        runs = self.results[name]
        wall_times = [r['wall_time'] for r in runs]
        cpu_times = [r['cpu_time'] for r in runs]

        stats = {
            'count': len(runs),
            'wall_time_mean': mean(wall_times),
            'wall_time_median': median(wall_times),
            'wall_time_min': min(wall_times),
            'wall_time_max': max(wall_times),
            'cpu_time_mean': mean(cpu_times),
            'cpu_time_median': median(cpu_times),
            'cpu_time_min': min(cpu_times),
            'cpu_time_max': max(cpu_times),
        }

        if len(wall_times) > 1:
            stats['wall_time_stdev'] = stdev(wall_times)
            stats['cpu_time_stdev'] = stdev(cpu_times)

        return stats

    def print_comparison(self):
        """
        Print comparison table of all tracked methods.
        """
        if not self.results:
            print("No results to compare")
            return

        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON")
        print("=" * 80)

        # Header
        print(f"\n{'Method':<20} {'Runs':<6} {'Avg Time (s)':<15} {'Min (s)':<12} {'Max (s)':<12}")
        print("-" * 80)

        # Sort by average time
        method_stats = []
        for name in self.results:
            stats = self.get_statistics(name)
            method_stats.append((name, stats))

        method_stats.sort(key=lambda x: x[1].get('wall_time_mean', float('inf')))

        # Print rows
        fastest_time = method_stats[0][1].get('wall_time_mean', 1.0) if method_stats else 1.0

        for name, stats in method_stats:
            avg_time = stats.get('wall_time_mean', 0)
            min_time = stats.get('wall_time_min', 0)
            max_time = stats.get('wall_time_max', 0)
            count = stats.get('count', 0)

            speedup = avg_time / fastest_time if fastest_time > 0 else 1.0

            print(f"{name:<20} {count:<6} {avg_time:<15.6f} {min_time:<12.6f} {max_time:<12.6f}", end='')
            if speedup > 1.0:
                print(f" ({speedup:.2f}x slower)")
            else:
                print(" (fastest)")

        print("=" * 80)

        # Show relative performance
        if len(method_stats) > 1:
            print("\nRelative Performance:")
            fastest_name = method_stats[0][0]
            print(f"  Baseline (fastest): {fastest_name}")

            for name, stats in method_stats[1:]:
                avg_time = stats.get('wall_time_mean', 0)
                speedup = avg_time / fastest_time
                percent_slower = (speedup - 1) * 100
                print(f"  {name}: {percent_slower:.1f}% slower")

    def save_results(self, filename: Optional[str] = None):
        """
        Save results to JSON file.

        Args:
            filename: Output filename. If None, generates timestamped name
        """
        if not self.config.get('save_results', True):
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_{timestamp}.json"

        results_dir = self.config.get('results_dir', 'output/performance')
        filepath = os.path.join(results_dir, filename)

        # Prepare data for export
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'results': self.results,
            'statistics': {name: self.get_statistics(name) for name in self.results}
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\nResults saved to: {filepath}")

    def clear(self):
        """Clear all results."""
        self.results.clear()
        self.metadata.clear()


# ============================================================================
# MEMORY PROFILING UTILITIES
# ============================================================================

def get_memory_usage() -> Dict[str, int]:
    """
    Get current memory usage.

    Returns:
        Dictionary with memory statistics (requires psutil)
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
        }
    except ImportError:
        return {'error': 'psutil not installed'}


@contextmanager
def memory_tracker(name: str = "Operation", verbose: bool = True):
    """
    Context manager for tracking memory usage.

    Usage:
        with memory_tracker("My Operation"):
            # ... code to track ...

    Args:
        name: Name of the operation
        verbose: Whether to print memory info
    """
    try:
        import psutil
    except ImportError:
        print("Warning: psutil not installed, memory tracking disabled")
        yield {}
        return

    process = psutil.Process()
    mem_before = process.memory_info()

    memory_info = {}

    try:
        yield memory_info
    finally:
        mem_after = process.memory_info()

        rss_diff = mem_after.rss - mem_before.rss
        vms_diff = mem_after.vms - mem_before.vms

        memory_info['rss_before'] = mem_before.rss
        memory_info['rss_after'] = mem_after.rss
        memory_info['rss_diff'] = rss_diff
        memory_info['vms_diff'] = vms_diff

        if verbose:
            print(f"\n[MEMORY] {name}:")
            print(f"  RSS Change: {rss_diff / 1024 / 1024:+.2f} MB")
            print(f"  VMS Change: {vms_diff / 1024 / 1024:+.2f} MB")
            print(f"  Current RSS: {mem_after.rss / 1024 / 1024:.2f} MB")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def compare_methods(methods: Dict[str, Callable], config: Optional[Dict] = None) -> PerformanceTracker:
    """
    Convenience function to compare multiple methods.

    Args:
        methods: Dictionary of {name: callable} to compare
        config: Optional configuration dict

    Returns:
        PerformanceTracker with results

    Usage:
        tracker = compare_methods({
            'method1': lambda: implementation1(),
            'method2': lambda: implementation2(),
        })
    """
    tracker = PerformanceTracker(config)

    for name, func in methods.items():
        print(f"\nTesting {name}...")
        tracker.track(name, func)

    tracker.print_comparison()
    return tracker
