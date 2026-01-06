"""
base_connector.py
-----------------
Abstract Interface for "Librarian" connectors.
Standardizes how we query external Knowledge Bases (AbuseIPDB, OTX, NVD).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseConnector(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Query the reputation of an IP address.
        Returns a dict with normalized fields:
            - score (0.0 to 1.0)
            - confidence (0.0 to 1.0)
            - tags (List[str])
            - description (str)
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Ping the API to ensure connectivity."""
        pass
