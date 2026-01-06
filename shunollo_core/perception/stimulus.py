from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

@dataclass
class Stimulus:
    """
    The Nerve Impulse.
    Standardized container for all sensory inputs entering the Brain.
    """
    source: str
    intensity: float = 0.0
    payload: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[List[float]] = None
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "intensity": self.intensity,
            "payload": self.payload,
            "metadata": self.metadata,
            "vector": self.vector,
            "timestamp": self.timestamp
        }
