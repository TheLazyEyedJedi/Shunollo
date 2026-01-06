from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class AbstractMemory(ABC):
    """
    The Brain's interface for storing/retrieving memories.
    It does NOT know about SQL, Redis, or File Systems.
    """
    
    @abstractmethod
    def store_event(self, event: Dict[str, Any], embedding: Optional[List[float]] = None) -> str:
        """Persist a cognitive event (history). Returns event ID."""
        pass
    
    @abstractmethod
    def recall_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent context (history)."""
        pass

    @abstractmethod
    def upsert_weight(self, agent: str, weight: float) -> None:
        """Update synaptic weights."""
        pass

    @abstractmethod
    def get_weight(self, agent: str) -> float:
        """Retrieve a specific agent's weight."""
        pass
    
    @abstractmethod
    def delete_weight(self, agent: str) -> None:
        """Remove an agent's weight."""
        pass
    
    @abstractmethod
    def get_all_weights(self) -> List[Dict[str, Any]]:
        """Retrieve all synaptic weights."""
        pass
    
    @abstractmethod
    def store_cluster(self, cluster: Dict[str, Any]) -> None:
        """Persist a perceptual cluster."""
        pass
    
    @abstractmethod
    def record_feedback(self, cluster_id: str, score: float, comment: str, tags: List[str]):
        """Record reinforcement learning feedback."""
        pass

    @abstractmethod
    def upsert_telemetry_bucket(self, bucket_start: int, conf: float, sound: float, light: float):
        """Update telemetry aggregations."""
        pass

    @abstractmethod
    def get_telemetry_history(self, seconds: int = 3600) -> List[Dict[str, Any]]:
        """Retrieve telemetry for charts."""
        pass
        
    @abstractmethod
    def get_artifacts(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Retrieve artifacts for an event."""
        pass
    
    @abstractmethod
    def get_correlation_id_by_event_id(self, event_id: str) -> Optional[str]:
        """Lookup correlation ID from event ID."""
        pass

    @abstractmethod
    def get_recent_cluster_feedback(self, limit: int = 60) -> List[Dict[str, Any]]:
        """Retrieve recent reinforcement learning feedback."""
        pass

    @abstractmethod
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent audit logs."""
        pass
    
    @abstractmethod
    def log_audit(self, action: str, details: str):
        """Write to the immutable audit log."""
        pass

    @abstractmethod
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit logs."""
        pass

    @abstractmethod
    def get_recent_cluster_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent feedback."""
        pass

    @abstractmethod
    def record_codon_feedback(self, agent: str, codon: str, feedback: str, score: float):
        """Record codon reinforcement."""
        pass

    @abstractmethod
    def get_codon_weights(self, agent: str) -> Dict[str, float]:
        """Retrieve learned weights for codons."""
        pass

    @abstractmethod
    def store_artifact(self, correlation_id: str, type_: str, filepath: str):
        """Link a file artifact to an event."""
        pass

    @abstractmethod
    def get_codon_memory(self, agent: str = None, codon: List[str] = None, feedback: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve raw codon feedback rows."""
        pass

    @abstractmethod
    def get_accumulated_feedback_stats(self, agent: str) -> Dict[str, int]:
        """Returns {'pos': int, 'neg': int, 'total': int} for an agent."""
        pass
    
    @abstractmethod
    def get_history_with_signatures(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Used for simulated accuracy calculation."""
        pass

    @abstractmethod
    def get_high_confidence_history(self, limit: int = 100, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Used for unsupervised drift calculation."""
        pass
