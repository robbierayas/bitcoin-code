"""
RIPEMD-160 Rollback Interface.

This module provides a high-level interface for attempting to reverse
RIPEMD-160 hash operations on Bitcoin addresses.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import signal
from rollback.bruteRipeMD160Mechanism import BruteRipeMD160Mechanism


class RollbackRipeMD160:
    """
    High-level interface for RIPEMD-160 rollback operations.

    This class provides a clean API for attempting to reverse RIPEMD-160
    operations on Bitcoin addresses using various mechanisms.
    """

    def __init__(self, address, mechanism_type='brute', max_iterations=None, progress_interval=1000):
        """
        Initialize the RIPEMD-160 rollback interface.

        Args:
            address: Bitcoin address to attempt rollback on
            mechanism_type: Type of rollback mechanism to use (default: 'brute')
            max_iterations: Maximum iterations before stopping (None = unlimited)
            progress_interval: How often to report progress (every N iterations)
        """
        self.address = address
        self.mechanism_type = mechanism_type
        self.mechanism = None
        self.result = None
        self.max_iterations = max_iterations
        self.progress_interval = progress_interval

        # Initialize the appropriate mechanism
        if mechanism_type == 'brute':
            self.mechanism = BruteRipeMD160Mechanism(
                address,
                max_iterations=max_iterations,
                progress_interval=progress_interval
            )
        else:
            raise ValueError(f"Unknown mechanism type: {mechanism_type}")

    def rollback(self, handle_interrupt=True):
        """
        Perform the rollback operation.

        This method executes the rollback mechanism and stores the result.
        Supports graceful interruption with Ctrl+C to print current stats.

        Args:
            handle_interrupt: Whether to install Ctrl+C handler (default: True)

        Returns:
            The result of the rollback operation
        """
        if self.mechanism is None:
            raise RuntimeError("No mechanism initialized")

        # Set up signal handler for graceful interruption
        old_handler = None
        if handle_interrupt:
            def signal_handler(sig, frame):
                print("\n\n[!] Interrupted by user (Ctrl+C)")
                print("Stopping gracefully and printing current stats...\n")
                self.mechanism.interrupted = True

            old_handler = signal.signal(signal.SIGINT, signal_handler)

        try:
            self.result = self.mechanism.run()
        finally:
            # Restore old signal handler
            if handle_interrupt and old_handler is not None:
                signal.signal(signal.SIGINT, old_handler)

        return self.result

    def run(self):
        """
        Execute the rollback (alias for rollback()).

        Returns:
            The result of the rollback operation
        """
        return self.rollback()

    def get_result(self):
        """
        Get the result of the last rollback operation.

        Returns:
            The stored result, or None if rollback hasn't been run yet
        """
        return self.result

    def set_verbose(self, verbose):
        """
        Set verbosity of the mechanism.

        Args:
            verbose: Boolean indicating whether to print diagnostic output
        """
        if self.mechanism and hasattr(self.mechanism, 'verbose'):
            self.mechanism.verbose = verbose


# Convenience function for backward compatibility
def myRollBack(address):
    """
    Convenience function for rollback (backward compatible with old interface).

    Args:
        address: Bitcoin address to attempt rollback on

    Returns:
        The result of the rollback operation
    """
    rollback = RollbackRipeMD160(address)
    return rollback.run()
