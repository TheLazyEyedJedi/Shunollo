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

    def to_vector(self, normalize: bool = True) -> List[float]:
        """
        Export physics vector for similarity search (Physics-RAG).
        This is the "fingerprint" of how this signal FELT.
        
        Args:
            normalize: If True, normalize fields to 0-1 range for fair distance comparison.
        
        Returns:
            18-dimensional physics vector.
        """
        # Raw values with their expected ranges for normalization
        raw = [
            (self.energy, 0.0, 10.0),       # 0: Amplitude (0-10 typical)
            (self.entropy, 0.0, 8.0),       # 1: Information Density (0-8 bits)
            (self.frequency, 0.0, 1000.0),  # 2: Rate (Hz, 0-1000 typical)
            (self.roughness, 0.0, 1.0),     # 3: Texture (already 0-1)
            (self.viscosity, 0.0, 1.0),     # 4: Flow Resistance (0-1)
            (self.volatility, 0.0, 1.0),    # 5: Brownian Deviation (0-1)
            (self.action, 0.0, 10.0),       # 6: Lagrangian (0-10)
            (self.hamiltonian, 0.0, 10.0),  # 7: Total Energy (0-10)
            (self.ewr, 0.0, 10.0),          # 8: Entropy-to-Wait Ratio (0-10)
            (self.hue, 0.0, 1.0),           # 9: Color/Spectrum (0-1)
            (self.saturation, 0.0, 1.0),    # 10: Purity (0-1)
            (self.pan, -1.0, 1.0),          # 11: Stereo Field (-1 to 1)
            (self.spatial_x, -1.0, 1.0),    # 12: 3D Space X (-1 to 1)
            (self.spatial_y, -1.0, 1.0),    # 13: 3D Space Y (-1 to 1)
            (self.spatial_z, -1.0, 1.0),    # 14: 3D Space Z (-1 to 1)
            (self.harmony, 0.0, 1.0),       # 15: Consonance (0-1)
            (self.flux, 0.0, 10.0),         # 16: Rate of Change (0-10)
            (self.dissonance, 0.0, 1.0),    # 17: Cross-Modal Conflict (0-1)
        ]
        
        if not normalize:
            return [v for v, _, _ in raw]
        
        # Normalize each field to 0-1 range
        normalized = []
        for value, min_val, max_val in raw:
            range_size = max_val - min_val
            if range_size == 0:
                normalized.append(0.0)
            else:
                # Clamp to range and normalize
                clamped = max(min_val, min(max_val, value))
                normalized.append((clamped - min_val) / range_size)
        return normalized


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
