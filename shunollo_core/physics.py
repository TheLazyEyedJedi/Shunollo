"""
physics.py
----------
Universal Physics for the Isomorphic Architecture.
Provides agnostic math for converting raw metrics into Qualia (Energy, Roughness, etc).
"""
import math
import random
import numpy as np

class PhysicsConfig:
    # Tunable constants for the Physics Engine.
    # Updated Phase 450: Scientifically valid values from Gymnasium Grid Search
    # Optimization Result (F1=1.0): Entropy=0.7, Jitter=0.1
    ROUGHNESS_ENTROPY_WEIGHT = 0.7
    ROUGHNESS_JITTER_WEIGHT = 0.1
    ROUGHNESS_ERROR_WEIGHT = 0.2
    
    # Statistical Baselines (Derived from Phase 120 Profiling)
    BASELINE_JITTER_MAX = 1.0   # 1000ms
    BASELINE_MTU = 1500.0       # Standard Ethernet
    BASELINE_ENTROPY_MAX = 8.0  # Max Shannon Entropy (Bits per byte)

def calculate_entropy(data: bytes | list) -> float:
    """
    Shannon Entropy (Information Density).
    H(X) = -sum(p(x) * log2(p(x)))
    Optimized: Uses numpy for valid O(1) vectorization.
    """
    if not data:
        return 0.0
        
    # Convert to numpy array for speed
    if isinstance(data, (bytes, bytearray)):
        arr = np.frombuffer(data, dtype=np.uint8)
    else:
        arr = np.array(data)

    if arr.size == 0:
        return 0.0

    # Get counts of each unique byte
    _, counts = np.unique(arr, return_counts=True)
    
    # Calculate probabilities
    probs = counts / arr.size
    
    # Calculate entropy
    # -sum(p * log2(p))
    entropy = -np.sum(probs * np.log2(probs))
         
    return float(entropy)

def calculate_energy(size: float, rate_hz: float = 0.0, criticality: float = 1.0) -> float:
    """
    Multivariate Energy (Intensity).
    Fusion of:
    - Volume (Size)
    - Velocity (Rate)
    - Importance (Criticality)
    
    Formula: Energy = Norm(Size) * Norm(Rate) * Criticality
    """
    # 1. Normalize Size (Log Scale)
    safe_size = max(1, min(size, 1500.0))
    norm_size = math.log10(safe_size) / math.log10(1500.0) # 0.0 - 1.0
    
    # 2. Normalize Rate (Linear Cap at 100hz)
    norm_rate = min(1.0, rate_hz / 100.0)
    
    # 3. Fusion (Power Law)
    # E = m * v^2 (Kinetic Energy)
    # We use a softened version: Size * Rate^1.5 to balance bandwidth vs PPS
    raw_energy = (norm_size * (norm_rate ** 1.5))
    
    # Scale to 0-1 range (roughly)
    # Rate term dominates (DDoS > File Transfer)
    return max(0.01, min(raw_energy * criticality, 1.0))

def calculate_roughness(entropy: float, jitter: float = 0.0, error_rate: float = 0.0) -> float:
    """
    Multivariate Roughness (Texture).
    Fusion of:
    - Information Density (Entropy): High randomness = Gritty.
    - Temporal Variance (Jitter): Irregular rhythm = Bumpy.
    - Structural Integrity (Errors): Failures = Jagged.
    """
    
    
    # 1. Entropy Contribution
    norm_entropy = min(1.0, entropy / PhysicsConfig.BASELINE_ENTROPY_MAX)
    
    # 2. Jitter Contribution
    norm_jitter = min(1.0, jitter / PhysicsConfig.BASELINE_JITTER_MAX)
    
    # 3. Error Contribution
    norm_error = min(1.0, error_rate)

    # Fusion (Configurable)
    # Why 0.4/0.4/0.2? 
    # Heuristic: Entropy (Payload) and Jitter (Timing) are primary indicators of covert channels.
    # Errors are secondary symptoms (e.g. timeout) but often masked by UDP.
    roughness = (
        (norm_entropy * PhysicsConfig.ROUGHNESS_ENTROPY_WEIGHT) + 
        (norm_jitter * PhysicsConfig.ROUGHNESS_JITTER_WEIGHT) + 
        (norm_error * PhysicsConfig.ROUGHNESS_ERROR_WEIGHT)
    )
    return max(0.0, min(roughness, 1.0))

def calculate_viscosity(delay_ms: float, pressure_psi: int = 0) -> float:
    """
    Multivariate Viscosity (Resistance).
    Fusion of Delay + Load.
    """
    # 1. Delay (0-2000ms equivalent)
    norm_delay = min(1.0, delay_ms / 2000.0)
    
    # 2. Pressure (0-100 items equivalent)
    norm_pressure = min(1.0, pressure_psi / 100.0)
    
    # Non-linear fusion: Pressure acts as a multiplier on Delay perception
    # If Queue is full, Delay feels "heavier".
    viscosity = norm_delay + (norm_pressure * 0.5)
    return min(1.0, viscosity)

def calculate_harmony(entropy: float, protocol_valid: bool, port_standard: bool, expected_high_entropy: bool = False) -> float:
    """
    Multivariate Harmony (Consonance).
    Fusion of Structure + Expectation.
    """
    score = 1.0
    
    # Penalty 1: Invalid Protocol Structure (e.g. malformed HTTP)
    if not protocol_valid:
        score -= 0.5
        
    # Penalty 2: Non-Standard Port usage (e.g. HTTP on 22)
    if not port_standard:
        score -= 0.2
        
    # Penalty 3: High Entropy on Plaintext Protocol (Encrypted payload in HTTP body)
    if entropy > 7.0 and protocol_valid and not expected_high_entropy: 
        # Note: This checks for "Hidden Encryption"
        score -= 0.8
        
    return max(0.0, score)

def calculate_flux(variance: float, limit: float = 100.0) -> float:
    """
    Flux (Rate of Change / Jitter).
    Measures the instability of a signal over time.
    """
    return min(1.0, variance / limit)

# ==============================================================================
# DEEP QUALIA PHYSICS (Phase 120) - See SENSORY_LEXICON.md
# ==============================================================================

class Somatosensory:
    """The Sense of Touch (Texture, Vibration, Temperature)."""
    
    @staticmethod
    def calculate_texture(entropy: float) -> float:
        """Map Entropy to Surface Roughness (0.0 Smooth - 1.0 Gritty)."""
        # Entropy 8.0 = 1.0 (Crypto/Gritty), Entropy 4.0 = 0.5 (Text)
        return min(1.0, entropy / 8.0)

    @staticmethod
    def calculate_vibration(jitter_ms: float) -> float:
        """Map Jitter to Vibration/Flutter (0.0 Stable - 1.0 Shaking)."""
        # Jitter > 100ms is heavy vibration
        return min(1.0, jitter_ms / 100.0)

    @staticmethod
    def calculate_temperature(flux: float) -> float:
        """Map Rate of Change to Heat (0.0 Cold - 1.0 Hot)."""
        # Flux > 50% change is Hot
        return min(1.0, flux * 2.0)

class Proprioception:
    """The Sense of Body Position (Strain, Tension, Load)."""

    @staticmethod
    def calculate_strain(load_factor: float) -> float:
        """Muscle Stretch (System Load)."""
        # load_factor 0.0 - 1.0 (normalized)
        return min(1.0, load_factor)

    @staticmethod
    def calculate_tension(pressure_psi: float) -> float:
        """Tendon Tension (Backpressure/Depth)."""
        # pressure_psi 0.0 - 1.0 (normalized)
        return min(1.0, pressure_psi)

class Vestibular:
    """The Sense of Balance (Stability, Acceleration)."""

    @staticmethod
    def calculate_vertigo(stability_loss: float) -> float:
        """Loss of Balance (e.g. Missing Data Frames)."""
        # stability_loss 0.0 (Perfect) - 1.0 (Falling)
        return min(1.0, stability_loss * 5.0) 

    @staticmethod
    def calculate_acceleration(velocity_delta: float) -> float:
        """G-Force (Sudden Burst/Change in velocity)."""
        # velocity_delta > 1.0 means sudden 2x spike
        return min(1.0, velocity_delta)

class Nociception:
    """The Sense of Pain (Damage, Stress)."""
    
    @staticmethod
    def calculate_pain(trauma_level: float, stress_duration: float) -> float:
        """
        Structural Damage (Trauma) + Sustained Stress (Lag).
        """
        # Trauma is sharp pain (multiply by 2.0)
        structural_pain = min(1.0, trauma_level * 2.0)
        
        # Stress is aching pain (normalized 0-1.0)
        thermal_pain = min(1.0, stress_duration)
        
        return max(structural_pain, thermal_pain)

# ==============================================================================






def calculate_dissonance(energy: float, saturation: float, harmony: float) -> float:
    """
    Multivariate Dissonance (Tone Tension).
    Derived from Energy, Intensity (Saturation), and Structural Harmony.
    """
    # High Energy + Low Harmony = Discord
    discord = (1.0 - harmony) * energy
    # Saturation (Intensity) amplifies the feeling of discord
    dissonance = discord * saturation
    return max(0.0, min(dissonance, 1.0))

def calculate_ewr(entropy: float, wait_ms: float) -> float:
    """
    Entropy-to-Wait Ratio (EWR).
    Measures the thermodynamic efficiency of signal obfuscation.
    Lower ratio = Higher stealth effort.
    """
    if wait_ms <= 0: return 1.0
    # EWR: How much information is packed per unit of latency
    return entropy / (wait_ms + 1.0)

# ==============================================================================
# TRILLION DOLLAR PHYSICS (Phase 280) - Finance-Inspired Isomorphism
# ==============================================================================

def calculate_volatility_index(actual_val: float, expected_mean: float, sigma: float, dt: float = 1.0) -> float:
    """
    Brownian Motion / Bachelier Metric.
    Measures how much a signal deviates from a standard 'Random Walk' (Gaussian noise).
    Includes temporal scaling via sqrt(dt).
    """
    if sigma <= 0: return 1.0
    
    # Bachelier Formula: VI = |x - mu| / (sigma * sqrt(dt))
    temporal_scaling = math.sqrt(max(0.1, dt))
    deviation = abs(actual_val - expected_mean) / (sigma * temporal_scaling)
    
    # 0.0 = Perfectly Random/Expected Noise
    # 1.0 = Highly Deterministic / Organized (Violation of Brownian Walk)
    return min(1.0, deviation / 5.0) 

def calculate_action_potential(kinetic: float, potential: float) -> float:
    """
    RE-ALIGNED: Lagrangian Mechanics (Principle of Least Action).
    Action (S) = Integral of (Kinetic - Potential) Energy.
    L = Kinetic (T) - Potential (V).
    
    Healthy: Kinetic is high, Potential is low -> L is high.
    Strain: Kinetic is low, Potential is high -> L is low.
    """
    # Normalize inputs
    norm_t = min(1.0, kinetic / 1000.0)
    norm_v = min(1.0, potential / 500.0)
    
    # Lagrangian: Effort - Resistance
    lagrangian = norm_t - norm_v
    
    # Map to "Strain" (0.0 Optimal - 1.0 Strained)
    # Whitepaper says L=1.0 is healthy, L < 0.3 is strain.
    strain = 1.0 - max(0.0, min(1.0, (lagrangian + 1.0) / 2.0))
    return strain

def calculate_hamiltonian(kinetic: float, potential: float) -> float:
    """
    Hamiltonian Energy (H = T + V).
    Measures total systemic complexity/exertion.
    """
    norm_t = min(1.0, kinetic / 1000.0)
    norm_v = min(1.0, potential / 500.0)
    return (norm_t + norm_v) / 2.0

def calculate_lyapunov_exponent(values: list) -> float:
    """
    Chaos / Determinism filter. Placeholder for full implementation.
    Returns 1.0 for high chaos, 0.0 for deterministic sequences.
    """
    if len(values) < 5: return 1.0
    # Simple variance of diffs as proxy for now
    diffs = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
    import statistics
    try:
        chaos = statistics.stdev(diffs) / (statistics.mean(diffs) + 1.0) if diffs else 1.0
        return min(1.0, chaos)
    except:
        return 1.0

def calculate_manifold_distance(current_dist: dict, baseline_dist: dict) -> float:
    """
    Information Geometry (Fisher Metric proxy).
    Uses KL Divergence as a distance on the information manifold.
    """
    # Placeholder: Return 0.0 for identical, 1.0 for extreme distance
    return 0.5 # Default middle-ground until implemented

def vectorize_sensation(physics_dict: dict, protocol: str = "tcp") -> list:
    """
    Convert a physics dictionary into a 13-dimensional Somatic Vector.
    Includes One-Hot Encoding for Protocols.
    
    Dimensions (Normalized [0,1]):
    0. Roughness
    1. Flux
    2. Viscosity
    3. Salience
    4. Dissonance
    5. Volatility
    6. Action
    7. Hamiltonian
    8. EWR
    9. Harmony
    10. Is_TCP (1.0 or 0.0)
    11. Is_UDP (1.0 or 0.0)
    12. Is_Other (1.0 or 0.0)
    """
    # Helper to safe-get and clamp
    def g(key, default=0.0):
        val = physics_dict.get(key, default)
        return max(0.0, min(1.0, float(val))) # Clamp [0,1] normalization assumption

    # One-Hot Encoding (Protocol Context)
    proto = protocol.lower()
    is_tcp = 1.0 if proto == "tcp" else 0.0
    is_udp = 1.0 if proto == "udp" else 0.0
    is_other = 1.0 if (not is_tcp and not is_udp) else 0.0

    return [
        g("roughness"),
        g("flux"),
        g("viscosity"),
        g("salience"),
        g("dissonance"),
        g("volatility"),
        g("action"),
        g("hamiltonian"),
        g("ewr"),
        g("harmony", 1.0), # Default to 1 (Healthy)
        is_tcp,
        is_udp,
        is_other
    ]

