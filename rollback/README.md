# Rollback System

This package provides tools and mechanisms for attempting to reverse cryptographic operations for educational and research purposes.

## Overview

The rollback system has been refactored into a clean, extensible architecture using abstract base classes and concrete implementations for different cryptographic algorithms. It includes comprehensive performance tracking utilities following Python best practices.

## Architecture

```
rollback/
├── rollbackMechanism.py          # Abstract base class
├── bruteRipeMD160Mechanism.py    # RIPEMD-160 brute force implementation
├── bruteECDSAMechanism.py        # ECDSA brute force placeholder
├── rollbackRipeMD160.py          # High-level RIPEMD-160 interface
├── rollbackECDSA.py              # High-level ECDSA interface
├── rollbackRunner.py             # Diagnostic runner with config-based output
├── performance.py                # Performance tracking utilities
├── run.py                        # Simple CLI interface (RECOMMENDED)
├── rollback_config.json          # Sample configuration file (DEPRECATED - use config.py)
├── example_usage.py              # Basic usage examples
├── performance_examples.py       # Performance tracking examples
├── README.md                     # This file
├── QUICKSTART.md                 # Quick start guide
└── CLI_GUIDE.md                  # Complete CLI documentation
```

## New Features

### Iteration Limiting (`--max-iterations`)

Stop execution after a specific number of iterations - perfect for performance testing:

```bash
python rollback/run.py key3 --max-iterations 5000
```

### Progress Reporting (`--progress-interval`)

Get periodic progress updates during execution:

```bash
python rollback/run.py key3 --max-iterations 10000 --progress-interval 500
# Reports progress every 500 iterations
```

### Graceful Interruption (Ctrl+C)

Press **Ctrl+C** at any time to gracefully stop and print current statistics:

```
[!] Interrupted by user (Ctrl+C)
Stopping gracefully and printing current stats...

======================================================================
CURRENT STATISTICS
======================================================================
Total Iterations:       2,345
findX_r Calls:          8
Brute Force Attempts:   891,234
X Values Found:         3

Stopped Early:          Yes
Stop Reason:            interrupted
======================================================================
```

### Statistics Tracking

All mechanisms automatically track:
- Total iterations completed
- Number of brute force attempts
- Values found
- Whether stopped early and why (max_iterations or interrupted)
- Detailed progress metrics

### ECDSA Support

Full CLI support for ECDSA rollback (currently placeholder implementation):

```bash
python rollback/run.py key1 --type ecdsa
python rollback/run.py 04abc... --type ecdsa --max-iterations 1000
```

## Configuration

**All configuration now lives in `config.py`** in the `RollbackConfig` class:

- `RollbackConfig.RUNNER_CONFIG`: Runner settings (verbose, logging, output)
- `RollbackConfig.RIPEMD160_CONFIG`: RIPEMD-160 mechanism settings
- `RollbackConfig.ECDSA_CONFIG`: ECDSA mechanism settings
- `RollbackConfig.PERFORMANCE_CONFIG`: Performance tracking settings
- `RollbackConfig.TEST_ADDRESSES`: Test addresses for rollback

## Class Hierarchy

```
RollbackMechanism (abstract)
    │
    ├── BruteRipeMD160Mechanism (concrete)
    │   │ - Implements reverse RIPEMD-160 operations
    │   │ - Tracks iterations, brute force attempts, X values found
    │   │ - Supports max_iterations and progress_interval
    │   │ - Handles Ctrl+C interruption gracefully
    │   └── Used by: RollbackRipeMD160
    │
    └── BruteECDSAMechanism (placeholder)
        │ - Placeholder for ECDSA private key recovery
        │ - Simulates iterations for framework demonstration
        │ - Same stats tracking as RIPEMD160 mechanism
        │ - Ready for future implementation (lattice attacks, etc.)
        └── Used by: RollbackECDSA
```

## Usage

### Basic RIPEMD-160 Rollback

```python
from rollback import RollbackRipeMD160

# Create rollback instance - uses config.py defaults
rollback = RollbackRipeMD160(address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')

# Run the rollback
result = rollback.run()

# Access results
print(result)
```

### Using Configuration from config.py

```python
from rollback import RollbackRunner
from config import RollbackConfig

# Runner automatically uses RollbackConfig.RUNNER_CONFIG
runner = RollbackRunner()

# Uses RollbackConfig.RIPEMD160_CONFIG for mechanism_type
result = runner.run_ripemd160(address)

# Override config if needed
custom_config = RollbackConfig.RUNNER_CONFIG.copy()
custom_config['verbose'] = False
runner = RollbackRunner(custom_config)
```

### Using the Diagnostic Runner

```python
from rollback import RollbackRunner

# Create runner with configuration
config = {
    'verbose': True,
    'log_to_file': True,
    'output_dir': 'output',
    'show_timing': True,
    'pretty_print': True
}

runner = RollbackRunner(config)

# Run RIPEMD-160 rollback with diagnostics
result = runner.run_ripemd160(
    address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    mechanism_type='brute'
)
```

## Performance Tracking

The rollback system includes comprehensive performance tracking utilities following Python best practices.

### Method 1: Simple Timing Decorator

```python
from rollback import timing_decorator, RollbackRipeMD160

@timing_decorator
def my_rollback():
    rollback = RollbackRipeMD160(address)
    return rollback.run()

result = my_rollback()  # Automatically prints execution time
```

### Method 2: Detailed Timing with CPU Time

```python
from rollback import detailed_timing_decorator

@detailed_timing_decorator(name="My Operation", enabled=True)
def my_rollback():
    # ... code ...
    pass

# Prints both wall time and CPU time
```

### Method 3: Context Manager for Specific Blocks

```python
from rollback import timer

with timer("Rollback Operation"):
    rollback = RollbackRipeMD160(address)
    result = rollback.run()
# Automatically prints timing when exiting context
```

### Method 4: Memory Tracking

```python
from rollback import memory_tracker

with memory_tracker("Memory Usage"):
    rollback = RollbackRipeMD160(address)
    result = rollback.run()
# Prints memory delta (requires psutil)
```

### Method 5: PerformanceTracker for Method Comparison

```python
from rollback import PerformanceTracker
from config import RollbackConfig

# Uses config.py settings automatically
tracker = PerformanceTracker()

# Track multiple runs
tracker.track('Method1', lambda: method1())
tracker.track('Method2', lambda: method2())
tracker.track('Method3', lambda: method3())

# Print comparison table
tracker.print_comparison()

# Save results to JSON
tracker.save_results('comparison.json')
```

### Method 6: Quick Comparison Function

```python
from rollback import compare_methods

methods = {
    'Implementation A': lambda: impl_a(),
    'Implementation B': lambda: impl_b(),
    'Implementation C': lambda: impl_c(),
}

tracker = compare_methods(methods)
# Automatically runs all methods and prints comparison
```

### Performance Configuration

Control performance tracking behavior in `config.py`:

```python
class RollbackConfig:
    PERFORMANCE_CONFIG = {
        'enabled': True,              # Enable performance tracking
        'track_memory': True,         # Track memory usage
        'track_cpu': True,            # Track CPU time
        'save_results': True,         # Save to file
        'results_dir': 'output/performance',
        'compare_methods': True,      # Enable comparison
        'warmup_runs': 0,            # Warmup iterations
        'repeat_runs': 1,            # Repeat for statistics
        'print_summary': True,        # Print after each test
    }
```

### Example Output

```
PERFORMANCE COMPARISON
================================================================================

Method               Runs   Avg Time (s)    Min (s)      Max (s)
--------------------------------------------------------------------------------
Quiet Output         3      2.345600        2.341200     2.350100 (fastest)
Verbose Output       3      2.456700        2.451300     2.462100 (1.05x slower)
Using Runner         3      2.567800        2.562400     2.573200 (1.09x slower)
================================================================================

Relative Performance:
  Baseline (fastest): Quiet Output
  Verbose Output: 4.7% slower
  Using Runner: 9.5% slower
```

### Command Line Interface

**NEW: Simple CLI with `run.py`** (Recommended)

```bash
# Interactive mode
python rollback/run.py

# List available test addresses
python rollback/run.py --list-tests

# RIPEMD-160 Rollback (default)
python rollback/run.py key1                              # Use test address
python rollback/run.py 1A1zP1e...                        # Custom address
python rollback/run.py key3 --quiet                      # Quiet mode
python rollback/run.py key3 --max-iterations 5000        # Limit iterations
python rollback/run.py key3 --progress-interval 500      # Progress every 500 iterations

# ECDSA Rollback (placeholder implementation)
python rollback/run.py key1 --type ecdsa                 # Use test key
python rollback/run.py 04abc... --type ecdsa             # Custom pubkey
python rollback/run.py key2 --type ecdsa --max-iterations 1000

# Performance Testing
python rollback/run.py --compare                         # Compare methods
python rollback/run.py --performance                     # Run performance tests

# Interruption Support
# Press Ctrl+C anytime during execution to gracefully stop and print current stats!
```

**Advanced: Direct `rollbackRunner.py`** (More options)

```bash
# Basic usage
python rollback/rollbackRunner.py ripemd160 <address>

# With verbose output
python rollback/rollbackRunner.py ripemd160 <address> --verbose

# With file logging
python rollback/rollbackRunner.py ripemd160 <address> --log

# Quiet mode
python rollback/rollbackRunner.py ripemd160 <address> --quiet
```

**See [CLI_GUIDE.md](CLI_GUIDE.md) for complete command-line documentation.**

### Configuration from config.py

All configuration is centralized in `config.py` for consistency:

```python
from config import RollbackConfig

# Runner configuration
print(RollbackConfig.RUNNER_CONFIG)
# {
#   'verbose': True,
#   'log_to_file': True,
#   'output_dir': 'output',
#   'show_timing': True,
#   'pretty_print': True
# }

# RIPEMD-160 configuration
print(RollbackConfig.RIPEMD160_CONFIG)
# {
#   'mechanism_type': 'brute',
#   'verbose': True,
#   'max_iterations': None
# }

# Performance tracking configuration
print(RollbackConfig.PERFORMANCE_CONFIG)
# {
#   'enabled': True,
#   'track_memory': True,
#   'warmup_runs': 0,
#   'repeat_runs': 1,
#   ...
# }

# Test addresses
print(RollbackConfig.TEST_ADDRESSES)
# {
#   'key1': "12vieiAHxBe4qCUrwvfb2kRkDuc8kQ8qSw",
#   'key2': "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM",
#   'key3': "1BTCorgHwCg6u2YSAWKgS17qUad6kHmtQW"
# }
```

## Components

### RollbackMechanism (Abstract Base Class)

Defines the interface for all rollback mechanisms:

- `__init__(target)`: Initialize with target data
- `run()`: Execute the rollback (abstract method)

### BruteRipeMD160Mechanism

Concrete implementation of brute force RIPEMD-160 rollback:

- Inherits from `RollbackMechanism`
- Attempts to reverse RIPEMD-160 hash operations
- Contains all RIPEMD-160 constants and helper functions
- Implements forward and reverse compression functions

### RollbackRipeMD160

High-level interface for RIPEMD-160 rollback:

- `__init__(address, mechanism_type='brute')`: Initialize with address
- `rollback()`: Perform rollback operation
- `run()`: Alias for `rollback()`
- `get_result()`: Get last rollback result
- `set_verbose(verbose)`: Control diagnostic output

### RollbackECDSA (Placeholder)

High-level interface for ECDSA rollback (not yet implemented):

- Same interface as `RollbackRipeMD160`
- Placeholder for future ECDSA attack implementations
- Ready for extension with mechanisms like:
  - Brute force key search
  - Lattice-based attacks
  - Side-channel analysis
  - Signature malleability

### RollbackRunner

Diagnostic runner with config-based output:

- `run_ripemd160(address, mechanism_type)`: Run RIPEMD-160 rollback
- `run_ecdsa(target, mechanism_type)`: Run ECDSA rollback
- Provides timing information
- Logs results to JSON files
- Pretty-prints output
- Command-line interface

## Backward Compatibility

The old `myRollBack()` function is still available for backward compatibility:

```python
from rollback.rollbackRipeMD160 import myRollBack

result = myRollBack(address)
```

## Examples

See `example_usage.py` for comprehensive examples:

```bash
python rollback/example_usage.py
```

## Migration from Old Structure

**Old code:**
```python
from cryptography.rollback import myRollBack
myRollBack(address)
```

**New code (recommended):**
```python
from rollback import RollbackRipeMD160
rollback = RollbackRipeMD160(address)
result = rollback.run()
```

**New code (backward compatible):**
```python
from rollback.rollbackRipeMD160 import myRollBack
myRollBack(address)
```

## Future Extensions

To add a new rollback mechanism:

1. Create a new mechanism class inheriting from `RollbackMechanism`
2. Implement the `run()` method
3. Create a high-level interface class (like `RollbackRipeMD160`)
4. Update the runner to support the new mechanism type

Example:

```python
from rollback.rollbackMechanism import RollbackMechanism

class MyCustomMechanism(RollbackMechanism):
    def run(self):
        # Implement your rollback logic here
        self.result = {...}
        return self.result
```

## Examples

### Basic Usage Examples

```bash
# Run basic rollback examples
python rollback/example_usage.py
```

This includes:
- Basic RIPEMD-160 rollback
- Quiet mode (no verbose output)
- Using the diagnostic runner
- ECDSA placeholder demo
- Backward compatibility

### Performance Tracking Examples

```bash
# Run all performance tracking examples
python rollback/performance_examples.py
```

This includes:
- Example 1: Simple timing decorator
- Example 2: Detailed timing with CPU time
- Example 3: Context manager for timing blocks
- Example 4: Memory tracking
- Example 5: PerformanceTracker with multiple runs
- Example 6: Comparing multiple methods
- Example 7: Quick comparison convenience function
- Example 8: Profiling different addresses
- Example 9: Combined time and memory tracking

### Quick Start

```python
# Simple rollback with config.py defaults
from rollback import RollbackRipeMD160
from config import RollbackConfig

address = RollbackConfig.TEST_ADDRESSES['key3']
rollback = RollbackRipeMD160(address)
result = rollback.run()
```

```python
# Compare two implementations
from rollback import compare_methods

methods = {
    'Method A': lambda: implementation_a(),
    'Method B': lambda: implementation_b(),
}

tracker = compare_methods(methods)
tracker.save_results('comparison.json')
```

## Best Practices for Performance Tracking

1. **Use Decorators** for function-level timing (non-intrusive)
2. **Use Context Managers** for timing specific code blocks
3. **Use PerformanceTracker** for comparing multiple implementations
4. **Configure warmup_runs** to stabilize caching effects (usually 1-3)
5. **Configure repeat_runs** for statistical significance (usually 3-10)
6. **Track both wall time and CPU time** to understand I/O vs computation
7. **Save results to JSON** for further analysis and visualization
8. **Use comparison tables** to identify fastest implementation
9. **Centralize config in config.py** for consistency across project
10. **Optional memory tracking** when investigating memory leaks

## Testing

Run the example scripts to test all functionality:

```bash
# Basic rollback examples
python rollback/example_usage.py

# Performance tracking examples
python rollback/performance_examples.py
```

## Performance Results Storage

Results are automatically saved to:
- `output/`: General rollback results (if log_to_file=True)
- `output/performance/`: Performance tracking results

JSON files include:
- Timestamp
- Configuration used
- Raw timing data for all runs
- Statistical analysis (mean, median, min, max, stdev)
- Method comparisons

## Notes

- This is experimental cryptographic research code
- Not intended for production use
- Use for educational and research purposes only
- See main CLAUDE.md for research context and warnings
- Performance tracking requires `psutil` for memory tracking (optional)
