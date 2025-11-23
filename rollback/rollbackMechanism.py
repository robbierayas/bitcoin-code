"""
Abstract base class for rollback mechanisms.

This module defines the interface that all rollback mechanisms must implement.
Rollback mechanisms attempt to reverse cryptographic operations for research purposes.
"""

from abc import ABC, abstractmethod


class RollbackMechanism(ABC):
    """
    Abstract base class for cryptographic rollback mechanisms.

    All rollback mechanisms should inherit from this class and implement
    the run() method with their specific attack/analysis logic.
    """

    def __init__(self, target):
        """
        Initialize the rollback mechanism.

        Args:
            target: The target data to attempt rollback on (format depends on mechanism)
        """
        self.target = target
        self.result = None

    @abstractmethod
    def run(self):
        """
        Execute the rollback mechanism.

        This method should perform the actual rollback/analysis and store
        the result in self.result.

        Returns:
            The result of the rollback attempt
        """
        pass
