"""
Rollback Diagnostic Runner.

This module provides a configurable diagnostic runner for testing rollback
mechanisms with detailed output and logging capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from datetime import datetime
from rollback.rollbackRipeMD160 import RollbackRipeMD160
from rollback.rollbackECDSA import RollbackECDSA
from config import RollbackConfig


class RollbackRunner:
    """
    Diagnostic runner for rollback mechanisms.

    Provides configurable testing with detailed output, timing, and result logging.
    """

    def __init__(self, config=None):
        """
        Initialize the rollback runner.

        Args:
            config: Dictionary containing configuration options. If None, uses
                   RollbackConfig.RUNNER_CONFIG from config.py.
                Options:
                - verbose: Print detailed output
                - log_to_file: Save results to file
                - output_dir: Directory for output files
                - show_timing: Show execution time
                - pretty_print: Pretty print results
        """
        # Use config.py defaults if no config provided
        self.config = config if config is not None else RollbackConfig.RUNNER_CONFIG.copy()

        self.verbose = self.config.get('verbose', True)
        self.log_to_file = self.config.get('log_to_file', False)
        self.output_dir = self.config.get('output_dir', 'output')
        self.show_timing = self.config.get('show_timing', True)
        self.pretty_print = self.config.get('pretty_print', True)

        # Create output directory if needed
        if self.log_to_file and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def run_ripemd160(self, address, mechanism_type=None, **kwargs):
        """
        Run RIPEMD-160 rollback with diagnostic output.

        Args:
            address: Bitcoin address to attempt rollback on
            mechanism_type: Type of mechanism to use. If None, uses
                          RollbackConfig.RIPEMD160_CONFIG['mechanism_type']
            **kwargs: Additional options to override config

        Returns:
            Dictionary containing results and metadata
        """
        # Use config.py defaults if not provided
        if mechanism_type is None:
            mechanism_type = RollbackConfig.RIPEMD160_CONFIG.get('mechanism_type', 'brute')
        if self.verbose:
            print("=" * 70)
            print("RIPEMD-160 ROLLBACK DIAGNOSTIC")
            print("=" * 70)
            print(f"Target Address: {address}")
            print(f"Mechanism Type: {mechanism_type}")
            print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 70)

        # Track timing
        import time
        start_time = time.time()

        try:
            # Create and run rollback
            rollback = RollbackRipeMD160(address, mechanism_type)
            rollback.set_verbose(self.verbose)
            result = rollback.run()

            # Calculate execution time
            execution_time = time.time() - start_time

            # Prepare output
            output = {
                'success': True,
                'address': address,
                'mechanism': mechanism_type,
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

            # Print results
            if self.verbose:
                print("-" * 70)
                print("RESULTS:")
                if self.pretty_print:
                    self._print_result(result)
                else:
                    print(result)

            if self.show_timing:
                print(f"\nExecution Time: {execution_time:.4f} seconds")

            # Log to file if configured
            if self.log_to_file:
                self._log_to_file('ripemd160', output)

            return output

        except Exception as e:
            execution_time = time.time() - start_time
            output = {
                'success': False,
                'address': address,
                'mechanism': mechanism_type,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

            if self.verbose:
                print(f"\nERROR: {e}")

            if self.show_timing:
                print(f"Execution Time: {execution_time:.4f} seconds")

            if self.log_to_file:
                self._log_to_file('ripemd160_error', output)

            return output

    def run_ecdsa(self, target, mechanism_type=None, **kwargs):
        """
        Run ECDSA rollback with diagnostic output.

        Args:
            target: Target data for rollback
            mechanism_type: Type of mechanism to use. If None, uses
                          RollbackConfig.ECDSA_CONFIG['mechanism_type']
            **kwargs: Additional options to override config

        Returns:
            Dictionary containing results and metadata
        """
        # Use config.py defaults if not provided
        if mechanism_type is None:
            mechanism_type = RollbackConfig.ECDSA_CONFIG.get('mechanism_type', 'brute')
        if self.verbose:
            print("=" * 70)
            print("ECDSA ROLLBACK DIAGNOSTIC")
            print("=" * 70)
            print(f"Target: {target}")
            print(f"Mechanism Type: {mechanism_type}")
            print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 70)

        # Track timing
        import time
        start_time = time.time()

        try:
            # Create and run rollback
            rollback = RollbackECDSA(target, mechanism_type)
            rollback.set_verbose(self.verbose)
            result = rollback.run()

            # Calculate execution time
            execution_time = time.time() - start_time

            # Prepare output
            output = {
                'success': True,
                'target': target,
                'mechanism': mechanism_type,
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

            # Print results
            if self.verbose:
                print("-" * 70)
                print("RESULTS:")
                if self.pretty_print:
                    self._print_result(result)
                else:
                    print(result)

            if self.show_timing:
                print(f"\nExecution Time: {execution_time:.4f} seconds")

            # Log to file if configured
            if self.log_to_file:
                self._log_to_file('ecdsa', output)

            return output

        except Exception as e:
            execution_time = time.time() - start_time
            output = {
                'success': False,
                'target': target,
                'mechanism': mechanism_type,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

            if self.verbose:
                print(f"\nERROR: {e}")

            if self.show_timing:
                print(f"Execution Time: {execution_time:.4f} seconds")

            if self.log_to_file:
                self._log_to_file('ecdsa_error', output)

            return output

    def _print_result(self, result):
        """Pretty print result dictionary."""
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for k, v in value.items():
                        if isinstance(v, int):
                            print(f"  {k}: {hex(v)}")
                        else:
                            print(f"  {k}: {v}")
                elif isinstance(value, list):
                    print(f"\n{key}:")
                    for i, item in enumerate(value):
                        if item != '':
                            if isinstance(item, int):
                                print(f"  [{i}]: {hex(item)}")
                            else:
                                print(f"  [{i}]: {item}")
                else:
                    print(f"{key}: {value}")
        else:
            print(result)

    def _log_to_file(self, prefix, output):
        """Save output to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        if self.verbose:
            print(f"\nResults saved to: {filepath}")


def load_config_from_file(config_path='rollback_config.json'):
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found, using defaults")
        return {}


if __name__ == '__main__':
    """
    Example usage and command-line interface.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Rollback Diagnostic Runner')
    parser.add_argument('type', choices=['ripemd160', 'ecdsa'], help='Rollback type')
    parser.add_argument('target', help='Target address or data')
    parser.add_argument('--mechanism', default='brute', help='Mechanism type (default: brute)')
    parser.add_argument('--config', help='Path to JSON config file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--log', action='store_true', help='Log results to file')
    parser.add_argument('--quiet', action='store_true', help='Suppress diagnostic output')

    args = parser.parse_args()

    # Load config
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = {}

    # Override with command-line args
    if args.verbose:
        config['verbose'] = True
    if args.log:
        config['log_to_file'] = True
    if args.quiet:
        config['verbose'] = False

    # Create runner
    runner = RollbackRunner(config)

    # Run appropriate rollback
    if args.type == 'ripemd160':
        result = runner.run_ripemd160(args.target, args.mechanism)
    elif args.type == 'ecdsa':
        result = runner.run_ecdsa(args.target, args.mechanism)

    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)
