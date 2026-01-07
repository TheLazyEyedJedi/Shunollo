from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def utc_now():
    return datetime.now(timezone.utc)

# ------------------------------------------------------------------ #
# Existing models                                                     (unchanged)
# ------------------------------------------------------------------ #
# ------------------------------------------------------------------ #
# Existing models                                                     (unchanged)
# ------------------------------------------------------------------ #
class ShunolloSignal(BaseModel):
    """
    The Universal Signal.
    A purely physical description of an event, decoupled from its source.
    """
    # 1. Identity
    input_type: str = "generic" # e.g. "network_packet", "audio_frame", "biometric_pulse"
    timestamp: Optional[datetime] = Field(default_factory=utc_now)
    
    # 2. Physics (The Isomorphism)
    # These are calculated by the Transducer before the Core sees it.
    energy: float = 0.0      # Amplitude/Volume
    entropy: float = 0.0     # Information Density (0.0 - 8.0)
    frequency: float = 0.0   # Pitch/Rate
    roughness: float = 0.0   # Texture/Entropy
    viscosity: float = 0.0   # Flow/Resistance
    volatility: float = 0.0  # Brownian Deviation (Bachelier Metric)
    action: float = 0.0      # Lagrangian Potential (Least Action)
    hamiltonian: float = 0.0 # Total Energy (H = T + V)
    ewr: float = 0.0         # Entropy-to-Wait Ratio (Stealth Metric)
    
    # 2b. The Kandinsky Fields (Color & Space)
    hue: float = 0.0         # Color/Spectrum (0.0 - 1.0 or 0-360)
    saturation: float = 0.0  # Purity
    pan: float = 0.0         # Stereo Field (-1.0 to 1.0)
    spatial_x: float = 0.0   # 3D Space X (-1.0 to 1.0)
    spatial_y: float = 0.0   # 3D Space Y (-1.0 to 1.0)
    spatial_z: float = 0.0   # 3D Space Z (-1.0 to 1.0)

    # 2c. Second-Order Physics (Derivatives & Relationships)
    # These capture the "Intelligence" of the signal (Harmony, Change)
    harmony: float = 0.0     # Consonance (Does Roughness match Frequency?)
    flux: float = 0.0        # Rate of Change (Delta Energy / Variance)
    dissonance: float = 0.0  # Cross-Modal Conflict (Energy vs Hue)
    
    # 3. Context
    metadata: Dict[str, Any] = Field(default_factory=dict) # Source data (payload, user_id, etc)

    def to_vector(self) -> List[float]:
        """
        Export 13-dimensional physics vector for similarity search (Physics-RAG).
        This is the "fingerprint" of how this signal FELT.
        """
        return [
            self.energy,      # 0: Amplitude
            self.entropy,     # 1: Information Density
            self.frequency,   # 2: Rate
            self.roughness,   # 3: Texture
            self.viscosity,   # 4: Flow Resistance
            self.volatility,  # 5: Brownian Deviation
            self.action,      # 6: Lagrangian
            self.hamiltonian, # 7: Total Energy
            self.ewr,         # 8: Entropy-to-Wait Ratio
            self.harmony,     # 9: Consonance
            self.flux,        # 10: Rate of Change
            self.dissonance,  # 11: Cross-Modal Conflict
            self.hue,         # 12: Color/Spectrum
        ]


class AgentResult(BaseModel):
    agent: str
    score: float
    reasoning: Optional[str] = None


class ManagerResult(BaseModel):
    classification: str
    confidence: float
    reason: Optional[str] = None


class AuditLogEntry(BaseModel):
    input_data: ShunolloSignal
    manager_result: ManagerResult
    agent_scores: Dict[str, AgentResult]
    timestamp: datetime = Field(default_factory=utc_now)

# ------------------------------------------------------------------ #
# NEW – Event-level model                                             (used by clusterer)
# ------------------------------------------------------------------ #
class EventCluster(BaseModel):
    id: str
    start_ts: datetime
    end_ts: datetime
    packet_ids: List[str]
    centroid: Tuple[float, float, float]  # (sound, light, confidence)
    severity: float
    signature: Optional[str] = None  # placeholder for future signature mapping
