# Rollback System - Quick Start

## 30-Second Quick Start

```bash
# List available test addresses
python rollback/run.py --list-tests

# Run a simple rollback
python rollback/run.py key3

# Run quietly (minimal output)
python rollback/run.py key3 --quiet

# Compare different methods
python rollback/run.py --compare
```

## 5 Most Common Commands

### 1. Interactive Mode
```bash
python rollback/run.py
```
Prompts you for what to do.

### 2. Quick Test with Test Address
```bash
python rollback/run.py key1    # or key2, key3
```
Uses pre-configured test addresses from config.py.

### 3. Custom Address
```bash
python rollback/run.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```
Works with any Bitcoin address.

### 4. Compare Methods (Performance)
```bash
python rollback/run.py --compare
```
Runs performance comparison of different implementations.

### 5. Quiet Mode
```bash
python rollback/run.py key3 --quiet
```
Minimal output - just shows results.

## Python API Quick Start

### Simple Rollback
```python
from rollback import RollbackRipeMD160

rollback = RollbackRipeMD160(address)
result = rollback.run()
```

### With Performance Tracking
```python
from rollback import timing_decorator

@timing_decorator
def my_rollback():
    rollback = RollbackRipeMD160(address)
    return rollback.run()

result = my_rollback()  # Automatically prints timing
```

### Compare Two Methods
```python
from rollback import compare_methods

methods = {
    'Method A': lambda: implementation_a(),
    'Method B': lambda: implementation_b(),
}

tracker = compare_methods(methods)
# Automatically prints comparison table
```

## Configuration

All configuration is in `config.py`:

```python
from config import RollbackConfig

# View current settings
print(RollbackConfig.RUNNER_CONFIG)
print(RollbackConfig.PERFORMANCE_CONFIG)

# Get test addresses
print(RollbackConfig.TEST_ADDRESSES)
```

## Output Locations

- `output/` - Rollback results (when logging enabled)
- `output/performance/` - Performance tracking results

## Next Steps

- **Full CLI Guide**: See [CLI_GUIDE.md](CLI_GUIDE.md)
- **Full Documentation**: See [README.md](README.md)
- **Examples**: Run `python rollback/example_usage.py`
- **Performance Examples**: Run `python rollback/performance_examples.py`

## Cheat Sheet

```bash
# HELP
python rollback/run.py --help

# LIST TESTS
python rollback/run.py --list-tests

# RUN ROLLBACK
python rollback/run.py key3                    # With output
python rollback/run.py key3 --quiet            # Quiet mode
python rollback/run.py key3 --runner           # With diagnostics

# PERFORMANCE
python rollback/run.py --compare               # Compare methods
python rollback/run.py --performance           # Test addresses

# INTERACTIVE
python rollback/run.py                         # Interactive mode

# CUSTOM ADDRESS
python rollback/run.py <your-address>
```

## Common Issues

**Import errors?**
```bash
pip install ecdsa pycryptodome
pip install psutil  # Optional, for memory tracking
```

**Module not found?**
```bash
# Run from project root
cd C:\Users\robbi\PycharmProjects\bitcoin-code
python rollback/run.py key3
```

**Want more control?**
```bash
# Use rollbackRunner.py directly
python rollback/rollbackRunner.py ripemd160 <address> --verbose --log
```
