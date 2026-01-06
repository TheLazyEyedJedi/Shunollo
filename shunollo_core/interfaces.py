"""
interfaces.py
-------------
Platform Interface definitions (ABC).
Defines the contract for external apps to interact with the Shunollo Brain.
"""
from abc import ABC, abstractmethod
from typing import Any
from shunollo_core.models import ShunolloSignal

class BaseTransducer(ABC):
    """
    Abstract base class for all sensory translators.
    """
    @abstractmethod
    def ingest(self, raw_data: Any) -> ShunolloSignal:
        """
        Convert raw input into a Universal ShunolloSignal.
        """
        pass
