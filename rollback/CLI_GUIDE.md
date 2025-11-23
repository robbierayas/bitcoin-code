# Rollback Command-Line Interface Guide

This guide explains all the ways to use the rollback system from the command line.

## Quick Start

### Simple Usage

```bash
# Interactive mode (prompts for input)
python rollback/run.py

# Use a test address
python rollback/run.py key1
python rollback/run.py key2
python rollback/run.py key3

# Use a custom Bitcoin address
python rollback/run.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### List Available Test Addresses

```bash
python rollback/run.py --list-tests
```

Output:
```
AVAILABLE TEST ADDRESSES
======================================================================

From RollbackConfig.TEST_ADDRESSES:
  key1: 12vieiAHxBe4qCUrwvfb2kRkDuc8kQ8qSw
  key2: 16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM
  key3: 1BTCorgHwCg6u2YSAWKgS17qUad6kHmtQW

Generate from TestKeys:
  KEY1: 1GAehh7TsJAHuUAeKZcXf5CnwuGuGgyX2S
  KEY2: 16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM
  KEY3: 1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
```

## Command-Line Options

### Basic Options

```bash
# Quiet mode (minimal output)
python rollback/run.py key3 --quiet

# Use RollbackRunner (includes diagnostic output)
python rollback/run.py key3 --runner
```

### Performance and Comparison

```bash
# Compare different rollback methods
python rollback/run.py --compare

# Run performance tests on multiple addresses
python rollback/run.py --performance
```

## Detailed Usage Examples

### Example 1: Simple Rollback

```bash
python rollback/run.py key3
```

Output shows:
- Configuration being used (from config.py)
- Progress of the rollback
- Results summary

### Example 2: Quiet Mode

```bash
python rollback/run.py key1 --quiet
```

Minimal output - just shows:
```
Running rollback for 12vieiAHxBe4qCUrwvfb2kRkDuc8kQ8qSw (quiet mode)...
✓ Complete. Found 8 values.
```

### Example 3: Compare Methods

```bash
python rollback/run.py --compare
```

Output shows:
```
METHOD COMPARISON MODE
======================================================================
Test Address: 1PE7Djw8d1RthCXNwyYYNBv89mmgVezsvy
Comparing 3 different methods...

[1/3] Testing Direct Rollback...
[2/3] Testing Via Runner...
[3/3] Testing With Mechanism Type...

PERFORMANCE COMPARISON
================================================================================
Method                   Runs   Avg Time (s)    Min (s)      Max (s)
--------------------------------------------------------------------------------
Direct Rollback          2      2.345600        2.341200     2.350100 (fastest)
Via Runner               2      2.456700        2.451300     2.462100 (1.05x slower)
With Mechanism Type      2      2.467800        2.462400     2.473200 (1.05x slower)
================================================================================
```

### Example 4: Performance Tests

```bash
python rollback/run.py --performance
```

Tests multiple addresses and compares performance.

### Example 5: Custom Address

```bash
python rollback/run.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

Works with any valid Bitcoin address.

## Interactive Mode

When run without arguments, enters interactive mode:

```bash
python rollback/run.py
```

Interactive menu:
```
ROLLBACK INTERACTIVE MODE
======================================================================

Options:
  1. Use a test address (key1, key2, key3)
  2. Enter a custom Bitcoin address
  3. Compare different methods
  4. Run performance tests
  5. Exit

Enter choice (1-5):
```

## Advanced Usage: Using rollbackRunner.py Directly

For more control, use `rollbackRunner.py` directly:

```bash
# Basic usage
python rollback/rollbackRunner.py ripemd160 <address>

# With options
python rollback/rollbackRunner.py ripemd160 <address> --verbose
python rollback/rollbackRunner.py ripemd160 <address> --log
python rollback/rollbackRunner.py ripemd160 <address> --quiet

# Specify mechanism type
python rollback/rollbackRunner.py ripemd160 <address> --mechanism brute

# Use custom config file (JSON)
python rollback/rollbackRunner.py ripemd160 <address> --config myconfig.json
```

## Configuration

All default configuration comes from `config.py`:

- `RollbackConfig.RUNNER_CONFIG` - Runner settings
- `RollbackConfig.RIPEMD160_CONFIG` - RIPEMD-160 mechanism settings
- `RollbackConfig.PERFORMANCE_CONFIG` - Performance tracking settings
- `RollbackConfig.TEST_ADDRESSES` - Pre-configured test addresses

To modify behavior, edit `config.py` or override on command line.

## Output Files

Results are saved to:
- `output/` - General rollback results (if logging enabled)
- `output/performance/` - Performance tracking results

JSON files include:
- Timestamp
- Configuration used
- Full results
- Execution time

## Common Workflows

### Quick Test

```bash
# Quick test with a known address
python rollback/run.py key3 --quiet
```

### Performance Analysis

```bash
# Compare implementations
python rollback/run.py --compare

# Test multiple addresses
python rollback/run.py --performance
```

### Development/Debugging

```bash
# Full verbose output
python rollback/run.py key3

# Using the runner with diagnostics
python rollback/run.py key3 --runner
```

### Production Run (if applicable)

```bash
# Quiet mode, log to file
python rollback/run.py <address> --quiet

# Check output/ directory for results
```

## Troubleshooting

### "Module not found" errors

Make sure you're running from the project root:
```bash
cd C:\Users\robbi\PycharmProjects\bitcoin-code
python rollback/run.py key3
```

### Import errors

Ensure all dependencies are installed:
```bash
pip install ecdsa pycryptodome
pip install psutil  # Optional, for memory tracking
```

### No output

If you see no output, the rollback might be running - be patient or use `--quiet` mode to see progress indicator.

## Help

Get help on any command:

```bash
# run.py help
python rollback/run.py --help

# rollbackRunner.py help
python rollback/rollbackRunner.py --help
```

## Examples Summary

```bash
# List tests
python rollback/run.py --list-tests

# Simple rollback
python rollback/run.py key3

# Quiet mode
python rollback/run.py key3 --quiet

# With diagnostics
python rollback/run.py key3 --runner

# Compare methods
python rollback/run.py --compare

# Performance tests
python rollback/run.py --performance

# Interactive mode
python rollback/run.py

# Custom address
python rollback/run.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Using rollbackRunner.py directly
python rollback/rollbackRunner.py ripemd160 key3 --verbose
```
