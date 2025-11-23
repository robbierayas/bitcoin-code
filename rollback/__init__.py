"""
Rollback package for cryptographic reverse engineering research.

This package provides tools and mechanisms for attempting to reverse
cryptographic operations for educational and research purposes.

Modules:
    - rollbackMechanism: Abstract base class for all rollback mechanisms
    - bruteRipeMD160Mechanism: Brute force RIPEMD-160 rollback implementation
    - rollbackRipeMD160: High-level interface for RIPEMD-160 rollback
    - rollbackECDSA: High-level interface for ECDSA rollback
    - rollbackRunner: Diagnostic runner with config-based output
    - performance: Performance tracking and comparison utilities
"""

from rollback.rollbackMechanism import RollbackMechanism
from rollback.bruteRipeMD160Mechanism import BruteRipeMD160Mechanism
from rollback.rollbackRipeMD160 import RollbackRipeMD160, myRollBack
from rollback.rollbackECDSA import RollbackECDSA
from rollback.rollbackRunner import RollbackRunner
from rollback.performance import (
    timing_decorator,
    detailed_timing_decorator,
    timer,
    memory_tracker,
    PerformanceTracker,
    compare_methods
)

__all__ = [
    # Rollback classes
    'RollbackMechanism',
    'BruteRipeMD160Mechanism',
    'RollbackRipeMD160',
    'RollbackECDSA',
    'RollbackRunner',
    'myRollBack',  # Backward compatibility

    # Performance tracking
    'timing_decorator',
    'detailed_timing_decorator',
    'timer',
    'memory_tracker',
    'PerformanceTracker',
    'compare_methods',
]
