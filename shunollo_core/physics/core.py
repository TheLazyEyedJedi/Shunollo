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

# ==============================================================================
# ADVANCED PHYSICS (Phase 500) - Neural Substrate Gap Implementations
# ==============================================================================

class Psychophysics:
    """
    Stevens' Power Law and Weber-Fechner for perceptual scaling.
    
    Different modalities have different exponents:
    - Brightness: 0.33 (compressive - wide dynamic range)
    - Loudness: 0.67 (moderately compressive)
    - Electric Shock: 3.5 (expansive - small change = big sensation)
    - Length: 1.0 (linear)
    
    Reference: Stevens, S. S. (1957). On the psychophysical law.
    """
    
    # Default exponents for different sensor modalities
    EXPONENTS = {
        "brightness": 0.33,
        "loudness": 0.67,
        "vibration": 0.95,
        "pressure": 1.1,
        "temperature": 1.0,
        "pain": 3.5,
        "latency": 1.5,      # Expansive: small delay feels big
        "throughput": 0.5,   # Compressive: big changes feel smaller
        "default": 1.0,
    }
    
    @staticmethod
    def apply_stevens_law(value: float, modality: str = "default") -> float:
        """
        Apply Stevens' Power Law: S = k * I^n
        
        Args:
            value: Normalized input intensity [0, 1]
            modality: Sensor type (determines exponent)
        
        Returns:
            Perceived sensation magnitude [0, 1]
        """
        n = Psychophysics.EXPONENTS.get(modality, 1.0)
        safe_value = max(0.0, min(1.0, value))
        
        if n == 1.0:
            return safe_value
        
        return safe_value ** n
    
    @staticmethod
    def calculate_jnd(intensity: float, weber_fraction: float = 0.1) -> float:
        """
        Just Noticeable Difference (Weber's Law).
        
        JND = k * I (where k is the Weber fraction)
        
        Args:
            intensity: Current stimulus intensity
            weber_fraction: Sensitivity constant (lower = more sensitive)
        
        Returns:
            The minimum detectable change
        """
        return intensity * weber_fraction


class VestibularDynamics:
    """
    Steinhausen torsion pendulum model for vestibular integration.
    
    The semicircular canals perform integration:
    Acceleration -> Velocity (via overdamped dynamics)
    
    This converts rate-based anomalies into cumulative state.
    """
    
    def __init__(self, damping: float = 0.85, time_constant: float = 10.0):
        """
        Args:
            damping: Damping coefficient [0, 1) - higher = more smoothing
            time_constant: Time constant in samples for decay
        """
        self.damping = damping
        self.time_constant = time_constant
        self._velocity = 0.0
        self._history = []
    
    def integrate_acceleration(self, acceleration: float) -> float:
        """
        Convert acceleration to velocity using overdamped dynamics.
        
        This is the Steinhausen model: the cupula displacement (and thus
        neural firing rate) is proportional to head velocity, not acceleration.
        
        Args:
            acceleration: Instantaneous acceleration (rate of change)
        
        Returns:
            Integrated velocity (cumulative state)
        """
        # Overdamped integration: velocity updates with damping
        self._velocity = self.damping * self._velocity + (1 - self.damping) * acceleration
        self._history.append(self._velocity)
        
        if len(self._history) > 100:
            self._history = self._history[-100:]
        
        return self._velocity
    
    def get_cumulative_displacement(self) -> float:
        """Get total accumulated displacement (double integration)."""
        if not self._history:
            return 0.0
        return sum(self._history) / len(self._history)
    
    def reset(self):
        """Reset integrator state."""
        self._velocity = 0.0
        self._history.clear()


class PoissonDetector:
    """
    Poisson statistics for quantum-limited signal detection.
    
    At low signal levels (photon counting, rare events), the fundamental
    limit is set by shot noise: variance = mean for Poisson processes.
    
    Reference: Hecht, Shlaer, Pirenne (1942) - Visual threshold experiment
    """
    
    def __init__(self, dark_noise: float = 0.01, threshold_events: int = 5):
        """
        Args:
            dark_noise: Background noise rate (false positives)
            threshold_events: Minimum coincident events to trigger detection
        """
        self.dark_noise = dark_noise
        self.threshold_events = threshold_events
    
    def detection_probability(self, mean_events: float) -> float:
        """
        Probability of detecting a signal given mean photon/event count.
        
        Uses cumulative Poisson distribution:
        P(detect) = P(n >= threshold) = 1 - sum(P(k)) for k=0 to threshold-1
        
        Args:
            mean_events: Expected number of events (lambda)
        
        Returns:
            Detection probability [0, 1]
        """
        import math
        
        if mean_events <= 0:
            return 0.0
        
        # Calculate P(n < threshold) = sum of P(k) for k=0 to threshold-1
        cumulative = 0.0
        for k in range(self.threshold_events):
            # Poisson: P(k) = (lambda^k * e^-lambda) / k!
            try:
                p_k = (mean_events ** k) * math.exp(-mean_events) / math.factorial(k)
                cumulative += p_k
            except OverflowError:
                break
        
        return 1.0 - cumulative
    
    def signal_to_noise(self, signal_events: float) -> float:
        """
        Calculate SNR for Poisson process.
        
        For shot-noise limited detection: SNR = signal / sqrt(signal + dark)
        
        Args:
            signal_events: Mean signal event count
        
        Returns:
            Signal-to-noise ratio
        """
        import math
        
        if signal_events <= 0:
            return 0.0
        
        total_events = signal_events + self.dark_noise
        noise = math.sqrt(total_events)
        
        return signal_events / noise if noise > 0 else 0.0
    
    def is_above_threshold(self, events: float, confidence: float = 0.95) -> bool:
        """Check if events exceed detection threshold with given confidence."""
        return self.detection_probability(events) >= confidence


class StressTensor:
    """
    Von Mises stress for detecting distortion vs uniform pressure.
    
    Uniform pressure (hydrostatic) causes volume change but no shape change.
    Distortion (deviatoric stress) causes shape change - this is what
    mechanoreceptors actually detect.
    
    Reference: Von Mises yield criterion in continuum mechanics.
    """
    
    @staticmethod
    def calculate_von_mises(sigma_1: float, sigma_2: float, sigma_3: float = 0.0) -> float:
        """
        Calculate Von Mises equivalent stress.
        
        sigma_vm = sqrt(0.5 * [(s1-s2)^2 + (s2-s3)^2 + (s3-s1)^2])
        
        Args:
            sigma_1, sigma_2, sigma_3: Principal stresses
        
        Returns:
            Von Mises stress (distortion measure)
        """
        import math
        
        term1 = (sigma_1 - sigma_2) ** 2
        term2 = (sigma_2 - sigma_3) ** 2
        term3 = (sigma_3 - sigma_1) ** 2
        
        return math.sqrt(0.5 * (term1 + term2 + term3))
    
    @staticmethod
    def is_distortion_anomaly(
        stresses: list, 
        uniform_threshold: float = 0.1
    ) -> tuple:
        """
        Detect if stress pattern indicates distortion (anomaly) vs uniform pressure.
        
        Uniform pressure: all stresses equal -> Von Mises = 0
        Distortion: unequal stresses -> Von Mises > 0
        
        Args:
            stresses: List of principal stresses (e.g., [cpu, memory, network])
            uniform_threshold: Threshold for considering stress "uniform"
        
        Returns:
            Tuple of (is_distortion, von_mises_value, mean_pressure)
        """
        if len(stresses) < 2:
            return False, 0.0, stresses[0] if stresses else 0.0
        
        # Pad to 3 stresses if needed
        s = list(stresses[:3]) + [0.0] * (3 - len(stresses))
        
        von_mises = StressTensor.calculate_von_mises(s[0], s[1], s[2])
        mean_pressure = sum(s) / len(s)
        
        # Normalize by mean to get relative distortion
        if mean_pressure > 0:
            relative_distortion = von_mises / mean_pressure
        else:
            relative_distortion = von_mises
        
        is_distortion = relative_distortion > uniform_threshold
        
        return is_distortion, von_mises, mean_pressure


class PropagationPhysics:
    """
    Cable theory: length constant (lambda) for signal propagation.
    
    Determines how far an anomaly propagates through a network before
    decaying to insignificance.
    
    lambda = sqrt(r_m / r_a) where r_m = membrane resistance, r_a = axial resistance
    """
    
    @staticmethod
    def calculate_length_constant(
        membrane_resistance: float, 
        axial_resistance: float
    ) -> float:
        """
        Calculate the length constant (lambda).
        
        Args:
            membrane_resistance: Resistance to "leakage" (isolation quality)
            axial_resistance: Resistance to "flow" (path resistance)
        
        Returns:
            Length constant (higher = further propagation)
        """
        import math
        
        if axial_resistance <= 0:
            return float('inf')
        
        return math.sqrt(membrane_resistance / axial_resistance)
    
    @staticmethod
    def signal_at_distance(
        initial_amplitude: float, 
        distance: float, 
        length_constant: float
    ) -> float:
        """
        Calculate signal amplitude at a given distance.
        
        V(x) = V_0 * exp(-x / lambda)
        
        Args:
            initial_amplitude: Signal strength at source
            distance: Distance from source
            length_constant: Decay parameter (lambda)
        
        Returns:
            Signal amplitude at distance
        """
        import math
        
        if length_constant <= 0:
            return 0.0
        
        return initial_amplitude * math.exp(-distance / length_constant)
    
    @staticmethod
    def propagation_radius(
        initial_amplitude: float, 
        threshold: float, 
        length_constant: float
    ) -> float:
        """
        Calculate how far a signal propagates before falling below threshold.
        
        Solves: threshold = initial * exp(-x / lambda) for x
        x = -lambda * ln(threshold / initial)
        
        Args:
            initial_amplitude: Signal strength at source
            threshold: Minimum detectable amplitude
            length_constant: Decay parameter
        
        Returns:
            Maximum propagation distance
        """
        import math
        
        if initial_amplitude <= threshold:
            return 0.0
        
        return length_constant * math.log(initial_amplitude / threshold)


class ImpedanceAnalyzer:
    """
    Acoustic impedance matching for protocol boundary analysis.
    
    When signals cross between different "media" (protocols, networks),
    impedance mismatch causes reflection (packet loss, retransmission).
    
    Reference: Middle ear transformer ratio in auditory physics.
    """
    
    @staticmethod
    def calculate_impedance(density: float, velocity: float) -> float:
        """
        Calculate characteristic impedance: Z = rho * c
        
        For networks: Z ~ bandwidth * latency (bandwidth-delay product)
        
        Args:
            density: "Mass" (data density, queue depth)
            velocity: "Speed" (throughput, bandwidth)
        
        Returns:
            Impedance value
        """
        return density * velocity
    
    @staticmethod
    def reflection_coefficient(z1: float, z2: float) -> float:
        """
        Calculate reflection coefficient at impedance boundary.
        
        R = ((Z2 - Z1) / (Z2 + Z1))^2
        
        Args:
            z1: Source impedance
            z2: Destination impedance
        
        Returns:
            Fraction of energy reflected [0, 1]
        """
        if z1 + z2 <= 0:
            return 1.0
        
        ratio = (z2 - z1) / (z2 + z1)
        return ratio ** 2
    
    @staticmethod
    def transmission_efficiency(z1: float, z2: float) -> float:
        """
        Calculate transmission efficiency (1 - reflection).
        
        Perfect match (Z1 = Z2) -> efficiency = 1.0
        Total mismatch -> efficiency = 0.0
        
        Args:
            z1: Source impedance
            z2: Destination impedance
        
        Returns:
            Transmission efficiency [0, 1]
        """
        return 1.0 - ImpedanceAnalyzer.reflection_coefficient(z1, z2)
    
    @staticmethod
    def required_transformer_ratio(z_source: float, z_load: float) -> float:
        """
        Calculate optimal transformer ratio for impedance matching.
        
        For perfect matching: ratio = sqrt(Z_load / Z_source)
        
        Args:
            z_source: Source impedance
            z_load: Load impedance
        
        Returns:
            Optimal transformer ratio
        """
        import math
        
        if z_source <= 0:
            return 1.0
        
        return math.sqrt(z_load / z_source)


# =============================================================================
# PHASE 2: BIOPHYSICS - Chemical, Thermal, Mechanical, Critical
# Reference: "The Physics of Transduction" (2026)
# =============================================================================

class ChemicalKinetics:
    """
    Chemical binding kinetics for saturation and concentration modeling.
    
    Two models:
    1. Hill-Langmuir: Sigmoidal receptor binding (θ = [L]^n / (Kd + [L]^n))
    2. Nernst: Logarithmic potential from ion concentration
    
    Reference: Section 6.2.1 - Thermodynamics of Receptor Binding
    """
    
    @staticmethod
    def hill_langmuir(
        concentration: float, 
        kd: float = 0.5, 
        hill_coefficient: float = 1.0
    ) -> float:
        """
        Calculate fractional occupancy using Hill-Langmuir equation.
        
        θ = [L]^n / (Kd + [L]^n)
        
        This models saturation behavior in:
        - Database connections (saturation at max pool)
        - API rate limits (sigmoidal degradation)
        - Memory usage (non-linear pressure)
        
        Args:
            concentration: Ligand/load concentration [0, ∞)
            kd: Dissociation constant (concentration at 50% saturation)
            hill_coefficient: Cooperativity (n=1: Michaelis-Menten, n>1: cooperative)
        
        Returns:
            Fractional occupancy [0, 1]
        """
        if concentration <= 0 or kd <= 0:
            return 0.0
        
        c_n = concentration ** hill_coefficient
        kd_n = kd ** hill_coefficient
        
        return c_n / (kd_n + c_n)
    
    @staticmethod
    def nernst_potential(
        concentration_inside: float,
        concentration_outside: float,
        valence: int = 1,
        temperature_kelvin: float = 310.0  # Body temp
    ) -> float:
        """
        Calculate equilibrium potential using Nernst equation.
        
        E = (RT/zF) * ln(C_out/C_in)
        
        For monovalent ions at 37°C: ~61.5 mV per decade
        
        This models:
        - Battery discharge curves
        - Resource depletion gradients
        - Concentration-driven flows
        
        Args:
            concentration_inside: Internal concentration
            concentration_outside: External concentration
            valence: Ion charge (1 for Na+/K+, 2 for Ca2+)
            temperature_kelvin: Temperature (310K = 37°C)
        
        Returns:
            Equilibrium potential in millivolts
        """
        import math
        
        if concentration_inside <= 0 or concentration_outside <= 0:
            return 0.0
        
        # Constants
        R = 8.314  # J/(mol·K) - Gas constant
        F = 96485  # C/mol - Faraday constant
        
        # Nernst: E = (RT/zF) * ln(C_out/C_in)
        # Convert to mV: multiply by 1000
        e_mv = (1000 * R * temperature_kelvin / (valence * F)) * math.log(
            concentration_outside / concentration_inside
        )
        
        return e_mv
    
    @staticmethod
    def binding_rate(
        concentration: float,
        k_on: float = 1.0,
        k_off: float = 0.1
    ) -> float:
        """
        Calculate steady-state binding rate.
        
        At equilibrium: rate = k_on * [L] / (k_on * [L] + k_off)
        
        Args:
            concentration: Ligand concentration
            k_on: Association rate constant
            k_off: Dissociation rate constant
        
        Returns:
            Binding rate [0, 1]
        """
        if k_on <= 0:
            return 0.0
        
        forward = k_on * concentration
        return forward / (forward + k_off)


class ThermoDynamics:
    """
    Temperature-dependent kinetics using Arrhenius equation.
    
    Models how reaction rates (and failure rates) depend exponentially
    on temperature via activation energy barriers.
    
    Reference: Section 7.2 - TRP Channels and Arrhenius Rate Theory
    """
    
    @staticmethod
    def arrhenius_rate(
        temperature_kelvin: float,
        activation_energy_j: float = 50000.0,  # ~50 kJ/mol typical
        pre_exponential: float = 1e13  # Attempt frequency (s^-1)
    ) -> float:
        """
        Calculate reaction rate using Arrhenius equation.
        
        k = A * exp(-Ea/RT)
        
        This models:
        - CPU/GPU thermal throttling risk
        - Component failure probability vs temperature
        - Chemical reaction rates
        
        Args:
            temperature_kelvin: Absolute temperature
            activation_energy_j: Activation energy in J/mol
            pre_exponential: Pre-exponential factor (attempt frequency)
        
        Returns:
            Reaction rate (units depend on A)
        """
        import math
        
        if temperature_kelvin <= 0:
            return 0.0
        
        R = 8.314  # Gas constant J/(mol·K)
        
        # Arrhenius: k = A * exp(-Ea/RT)
        exponent = -activation_energy_j / (R * temperature_kelvin)
        
        # Clamp to prevent overflow
        exponent = max(-700, min(700, exponent))
        
        return pre_exponential * math.exp(exponent)
    
    @staticmethod
    def q10_coefficient(
        rate_t1: float,
        rate_t2: float,
        delta_temp: float = 10.0
    ) -> float:
        """
        Calculate Q10 coefficient (rate change per 10°C).
        
        Q10 = (k2/k1)^(10/(T2-T1))
        
        Typical values:
        - Enzymes: Q10 ≈ 2 (doubles per 10°C)
        - TRP channels: Q10 > 10 (extremely steep)
        
        Args:
            rate_t1: Rate at temperature 1
            rate_t2: Rate at temperature 2
            delta_temp: Temperature difference (T2 - T1)
        
        Returns:
            Q10 coefficient
        """
        import math
        
        if rate_t1 <= 0 or rate_t2 <= 0 or delta_temp == 0:
            return 1.0
        
        ratio = rate_t2 / rate_t1
        exponent = 10.0 / delta_temp
        
        return ratio ** exponent
    
    @staticmethod
    def thermal_failure_probability(
        temperature_celsius: float,
        threshold_celsius: float = 85.0,
        sensitivity: float = 0.1
    ) -> float:
        """
        Calculate failure probability based on temperature.
        
        Uses a sigmoid based on distance from thermal threshold.
        
        Args:
            temperature_celsius: Current temperature
            threshold_celsius: Critical temperature (Tjmax)
            sensitivity: Steepness of transition
        
        Returns:
            Failure probability [0, 1]
        """
        import math
        
        delta = temperature_celsius - threshold_celsius
        
        # Sigmoid centered at threshold
        try:
            return 1.0 / (1.0 + math.exp(-sensitivity * delta))
        except OverflowError:
            return 1.0 if delta > 0 else 0.0


class MechanoFilter:
    """
    Viscoelastic mechanical filtering (Pacinian Corpuscle model).
    
    Implements a high-pass filter that ignores static pressure but
    responds to rapid changes (texture, vibration).
    
    Transfer function: H(s) = sτ / (1 + sτ)
    
    Reference: Section 5.2.1 - The Pacinian Corpuscle: Mechanical Filtering
    """
    
    def __init__(self, time_constant: float = 0.05):
        """
        Args:
            time_constant: τ in seconds (50ms typical for Pacinian)
        """
        self.tau = time_constant
        self._prev_input = 0.0
        self._prev_output = 0.0
    
    def filter(self, input_value: float, dt: float = 0.01) -> float:
        """
        Apply viscoelastic high-pass filter.
        
        Discrete approximation of: H(s) = sτ / (1 + sτ)
        
        This creates "rapid adaptation":
        - Static pressure: output decays to zero
        - Vibration/texture: output tracks derivative
        
        Args:
            input_value: Current input (pressure, load, etc.)
            dt: Time step in seconds
        
        Returns:
            Filtered output (derivative-like)
        """
        if dt <= 0:
            dt = 0.01
        
        # High-pass filter: y[n] = α * (y[n-1] + x[n] - x[n-1])
        # where α = τ / (τ + dt)
        alpha = self.tau / (self.tau + dt)
        
        output = alpha * (self._prev_output + input_value - self._prev_input)
        
        self._prev_input = input_value
        self._prev_output = output
        
        return output
    
    def reset(self):
        """Reset filter state."""
        self._prev_input = 0.0
        self._prev_output = 0.0
    
    @staticmethod
    def adaptation_time_constant(
        capsule_layers: int = 30,
        fluid_viscosity: float = 1.0
    ) -> float:
        """
        Estimate time constant from physical parameters.
        
        More layers and higher viscosity = longer time constant.
        
        Args:
            capsule_layers: Number of concentric layers
            fluid_viscosity: Relative viscosity of interstitial fluid
        
        Returns:
            Estimated time constant in seconds
        """
        # Empirical relationship: τ ≈ 0.002 * layers * viscosity
        return 0.002 * capsule_layers * fluid_viscosity


class CriticalResonator:
    """
    Hopf Bifurcation model for active amplification near criticality.
    
    The cochlear amplifier operates at the edge of oscillation,
    providing 40-60 dB gain for weak signals while compressing
    strong signals. This allows detection below the thermal noise floor.
    
    Reference: Section 3.2.2 - The Active Process and Negative Stiffness
    """
    
    def __init__(
        self, 
        natural_frequency: float = 1.0,
        damping: float = 0.01,  # Very low = near critical point
        nonlinear_coefficient: float = 1.0
    ):
        """
        Args:
            natural_frequency: ω0 (resonant frequency)
            damping: ζ (damping ratio, <0.1 for near-critical)
            nonlinear_coefficient: β (Duffing-type saturation)
        """
        self.omega0 = natural_frequency
        self.zeta = damping
        self.beta = nonlinear_coefficient
        self._amplitude = 0.0
        self._phase = 0.0
    
    def gain(self, input_amplitude: float) -> float:
        """
        Calculate the compression gain at current amplitude.
        
        Near Hopf bifurcation:
        - Weak signals: Gain → 1/ζ (very high for small ζ)
        - Strong signals: Gain → 1/β*A² (compressed)
        
        This produces the characteristic 1/3 power law compression.
        
        Args:
            input_amplitude: Input signal amplitude
        
        Returns:
            Gain factor (can be >> 1 for weak signals)
        """
        import math
        
        if input_amplitude <= 0:
            return 0.0
        
        # At low amplitude: linear regime, gain = 1/(2*zeta)
        # At high amplitude: compressed, gain ∝ input^(-2/3)
        
        linear_gain = 1.0 / (2.0 * self.zeta) if self.zeta > 0 else 100.0
        
        # Crossover amplitude where nonlinearity takes over
        crossover = self.zeta / self.beta if self.beta > 0 else 1.0
        
        if input_amplitude < crossover:
            # Linear regime: high gain
            return linear_gain
        else:
            # Compressed regime: gain decreases with amplitude
            # Gain ∝ (crossover/amplitude)^(2/3)
            return linear_gain * (crossover / input_amplitude) ** (2.0 / 3.0)
    
    def amplify(self, input_signal: float) -> float:
        """
        Apply active amplification with compression.
        
        Args:
            input_signal: Input signal value
        
        Returns:
            Amplified output (compressed for large inputs)
        """
        amplitude = abs(input_signal)
        gain = self.gain(amplitude)
        
        # Apply gain with sign preservation
        return input_signal * gain
    
    def sensitivity_enhancement(self) -> float:
        """
        Calculate the sensitivity enhancement factor.
        
        Returns:
            dB improvement over passive system
        """
        import math
        
        # Enhancement = 20 * log10(1/(2*zeta))
        if self.zeta <= 0:
            return 60.0  # Max realistic
        
        enhancement_db = 20.0 * math.log10(1.0 / (2.0 * self.zeta))
        return min(60.0, max(0.0, enhancement_db))
    
    def is_near_bifurcation(self) -> bool:
        """
        Check if system is operating near critical point.
        
        Returns:
            True if damping is low enough for active amplification
        """
        return self.zeta < 0.1


# =============================================================================
# PHASE 3: ELECTRONIC CONVERGENCE - Sensor Physics, Factor Graphs, Distortion
# Reference: "The Convergence of Electronic Instrumentation and Biological Perception"
# =============================================================================

class NoisePhysics:
    """
    Allan Variance noise characterization for sensor/signal stability analysis.
    
    The Allan Variance identifies 5 canonical noise types based on their
    slope on a log-log plot of sigma vs averaging time (tau):
        - Quantization: slope -1
        - Random Walk (ARW/VRW): slope -1/2
        - Bias Instability: slope 0 (flat)
        - Rate Random Walk: slope +1/2
        - Drift Ramp: slope +1
    
    Reference: IEEE Std 952-1997, Section 1.1.2 of Convergence Report
    """
    
    # Canonical noise types and their log-log slopes
    NOISE_TYPES = {
        'quantization': -1.0,
        'random_walk': -0.5,
        'bias_instability': 0.0,
        'rate_random_walk': 0.5,
        'drift_ramp': 1.0,
    }
    
    @staticmethod
    def allan_variance(samples: list, sample_rate: float = 1.0) -> dict:
        """
        Compute Allan Variance for multiple averaging times.
        
        σ²_A(τ) = (1/2) * <(y_{k+1} - y_k)²>
        
        Args:
            samples: Time series of sensor readings
            sample_rate: Samples per second
        
        Returns:
            Dict of {tau: sigma} pairs for plotting
        """
        import numpy as np
        
        n = len(samples)
        if n < 4:
            return {}
        
        data = np.array(samples, dtype=float)
        results = {}
        
        # Compute for powers of 2 averaging times
        max_m = n // 4
        m = 1
        while m <= max_m:
            tau = m / sample_rate
            
            # Compute non-overlapping averages
            num_bins = n // m
            if num_bins < 2:
                break
            
            # Reshape and average
            truncated = data[:num_bins * m]
            averages = truncated.reshape(-1, m).mean(axis=1)
            
            # Allan variance = 0.5 * mean(diff²)
            diffs = np.diff(averages)
            avar = 0.5 * np.mean(diffs ** 2)
            adev = np.sqrt(avar) if avar > 0 else 0.0
            
            results[tau] = adev
            m *= 2
        
        return results
    
    @staticmethod
    def classify_noise(allan_results: dict) -> tuple:
        """
        Classify the dominant noise type from Allan Variance results.
        
        Uses linear regression on log-log data to determine slope.
        
        Args:
            allan_results: Dict from allan_variance()
        
        Returns:
            Tuple of (noise_type: str, slope: float, confidence: float)
        """
        import numpy as np
        
        if len(allan_results) < 3:
            return ('unknown', 0.0, 0.0)
        
        taus = np.array(list(allan_results.keys()))
        sigmas = np.array(list(allan_results.values()))
        
        # Filter out zeros
        mask = sigmas > 0
        if np.sum(mask) < 3:
            return ('unknown', 0.0, 0.0)
        
        log_tau = np.log10(taus[mask])
        log_sigma = np.log10(sigmas[mask])
        
        # Linear regression: log(sigma) = slope * log(tau) + intercept
        coeffs = np.polyfit(log_tau, log_sigma, 1)
        slope = coeffs[0]
        
        # Calculate R² for confidence
        predicted = np.polyval(coeffs, log_tau)
        ss_res = np.sum((log_sigma - predicted) ** 2)
        ss_tot = np.sum((log_sigma - np.mean(log_sigma)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Find closest canonical noise type
        best_type = 'unknown'
        min_distance = float('inf')
        
        for noise_type, canonical_slope in NoisePhysics.NOISE_TYPES.items():
            distance = abs(slope - canonical_slope)
            if distance < min_distance:
                min_distance = distance
                best_type = noise_type
        
        return (best_type, float(slope), float(r_squared))
    
    @staticmethod
    def generate_noise(noise_type: str, n_samples: int, amplitude: float = 1.0) -> list:
        """
        Generate synthetic noise of a specific type for simulation.
        
        Args:
            noise_type: One of the canonical types
            n_samples: Number of samples to generate
            amplitude: Scale factor
        
        Returns:
            List of noise samples
        """
        import numpy as np
        
        if noise_type == 'random_walk':
            # Integrate white noise
            white = np.random.randn(n_samples) * amplitude
            return list(np.cumsum(white))
        
        elif noise_type == 'bias_instability':
            # First-order Gauss-Markov (correlated noise)
            beta = 0.1  # Correlation time constant
            noise = np.zeros(n_samples)
            for i in range(1, n_samples):
                noise[i] = (1 - beta) * noise[i-1] + beta * np.random.randn() * amplitude
            return list(noise)
        
        elif noise_type == 'drift_ramp':
            # Linear trend + white noise
            t = np.linspace(0, 1, n_samples)
            return list(t * amplitude + np.random.randn(n_samples) * 0.1 * amplitude)
        
        elif noise_type == 'rate_random_walk':
            # Double integration of white noise
            white = np.random.randn(n_samples) * amplitude
            return list(np.cumsum(np.cumsum(white)))
        
        else:  # Quantization or default white
            return list(np.random.randn(n_samples) * amplitude)
    
    @staticmethod
    def sensor_health(allan_results: dict) -> tuple:
        """
        Assess sensor health based on noise profile.
        
        Returns:
            Tuple of (health_score: 0-1, diagnosis: str)
        """
        noise_type, slope, confidence = NoisePhysics.classify_noise(allan_results)
        
        if noise_type == 'random_walk':
            return (0.9, "Normal: White noise floor")
        elif noise_type == 'bias_instability':
            return (0.7, "Caution: Bias drifting, recalibration may help")
        elif noise_type == 'rate_random_walk':
            return (0.4, "Warning: Hardware aging, replacement recommended")
        elif noise_type == 'drift_ramp':
            return (0.2, "Critical: Systematic drift, sensor failing")
        else:
            return (0.5, f"Unknown: slope={slope:.2f}, confidence={confidence:.2f}")


class FactorGraph:
    """
    Simple Factor Graph for constraint-based episodic memory optimization.
    
    Unlike Physics-RAG (pure vector search), Factor Graphs enforce
    consistency between connected memories. If A implies B, then
    recalling A must strengthen B's probability.
    
    Reference: Section 3.2 - Factor Graphs and Smoothing
    """
    
    def __init__(self):
        """Initialize empty factor graph."""
        self.nodes = {}  # node_id -> state_vector
        self.factors = []  # list of dicts: {type, nodes, params}
        self._node_id = 0
    
    def add_node(self, state: list, timestamp: float = 0.0) -> int:
        """
        Add a state node to the graph.
        
        Args:
            state: State vector (e.g., physics vector)
            timestamp: Time of observation
        
        Returns:
            Node ID
        """
        import numpy as np
        
        node_id = self._node_id
        self.nodes[node_id] = {
            'state': np.array(state, dtype=float),
            'timestamp': timestamp,
            'confidence': 1.0,
        }
        self._node_id += 1
        return node_id
    
    def add_temporal_constraint(self, node_a: int, node_b: int, expected_delta: list = None):
        """
        Add temporal consistency constraint between nodes.
        
        Enforces that node_b should follow node_a with expected change.
        """
        import numpy as np
        if expected_delta is None:
            expected_delta = [] # Handle in logic
            
        self.factors.append({
            'type': 'temporal',
            'nodes': [node_a, node_b],
            'params': {'delta': np.array(expected_delta) if expected_delta else None}
        })
    
    def add_similarity_constraint(self, node_a: int, node_b: int, max_distance: float = 0.5):
        """
        Add similarity constraint between nodes (they should look alike).
        """
        self.factors.append({
            'type': 'similarity',
            'nodes': [node_a, node_b],
            'params': {'max_dist': max_distance}
        })
    
    def compute_energy(self) -> float:
        """
        Compute total graph energy (sum of squared residuals).
        """
        import numpy as np
        total = 0.0
        
        for factor in self.factors:
            node_ids = factor['nodes']
            if not all(nid in self.nodes for nid in node_ids):
                continue
            
            states = [self.nodes[nid]['state'] for nid in node_ids]
            
            if factor['type'] == 'temporal':
                # Residual = ||(b - a) - delta||
                delta = factor['params']['delta']
                if delta is None: 
                    delta = np.zeros_like(states[0])
                
                diff = states[1] - states[0]
                residual = np.linalg.norm(diff - delta)
                total += residual ** 2
                
            elif factor['type'] == 'similarity':
                # Residual = max(0, ||a - b|| - max_dist)
                dist = np.linalg.norm(states[0] - states[1])
                max_dist = factor['params']['max_dist']
                residual = max(0, dist - max_dist)
                total += residual ** 2
                
        return total
    
    def optimize(self, iterations: int = 10, learning_rate: float = 0.1) -> float:
        """
        Optimize node states to minimize total energy using Analytical Gradients.
        """
        import numpy as np
        
        for _ in range(iterations):
            gradients = {nid: np.zeros_like(self.nodes[nid]['state']) 
                        for nid in self.nodes}
            
            for factor in self.factors:
                node_ids = factor['nodes']
                if not all(nid in self.nodes for nid in node_ids):
                    continue
                
                nid_a, nid_b = node_ids[0], node_ids[1]
                vec_a = self.nodes[nid_a]['state']
                vec_b = self.nodes[nid_b]['state']
                
                if factor['type'] == 'temporal':
                    # E = ||x_b - x_a - delta||^2
                    # dE/db = 2 * (x_b - x_a - delta)
                    # dE/da = -2 * (x_b - x_a - delta)
                    
                    delta = factor['params']['delta']
                    if delta is None: 
                        delta = np.zeros_like(vec_a)
                    
                    error_vec = vec_b - vec_a - delta
                    grad = 2.0 * error_vec
                    
                    gradients[nid_b] += grad
                    gradients[nid_a] -= grad
                    
                elif factor['type'] == 'similarity':
                    # E = max(0, ||a - b|| - max)^2
                    # Let u = ||a - b|| - max
                    # If u <= 0, E=0, grad=0
                    # If u > 0, E = u^2
                    # dE/u = 2u
                    # du/da = d(||a-b||)/da = (a-b) / ||a-b||
                    
                    diff = vec_a - vec_b
                    dist = np.linalg.norm(diff)
                    max_dist = factor['params']['max_dist']
                    
                    if dist > max_dist and dist > 1e-9:
                        u = dist - max_dist
                        # Scalar derivative dE/du
                        dE_du = 2.0 * u
                        # Vector derivative du/da (direction)
                        du_da = diff / dist
                        
                        grad = dE_du * du_da
                        
                        gradients[nid_a] += grad
                        gradients[nid_b] -= grad
            
            # Apply gradients
            for nid in self.nodes:
                self.nodes[nid]['state'] -= learning_rate * gradients[nid]
        
        return self.compute_energy()
    
    def get_trajectory(self) -> list:
        """
        Get all states sorted by timestamp.
        
        Returns:
            List of (timestamp, state) tuples
        """
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x['timestamp'])
        return [(n['timestamp'], n['state'].tolist()) for n in sorted_nodes]


class DistortionModel:
    """
    Brown-Conrady distortion model for data "lens" effects.
    
    Real data pipelines have distortions similar to camera lenses:
    - Center (high priority) is linear/undistorted
    - Periphery (low priority) is compressed/warped
    
    This models how attention and priority create perception distortion.
    
    Reference: Section 1.2.2 - Brown-Conrady Distortion Model
    """
    
    def __init__(
        self,
        k1: float = 0.0,   # Radial distortion (barrel if >0, pincushion if <0)
        k2: float = 0.0,   # Higher-order radial
        k3: float = 0.0,   # Even higher-order
        p1: float = 0.0,   # Tangential (decentering)
        p2: float = 0.0,
    ):
        """
        Initialize distortion coefficients.
        
        Args:
            k1, k2, k3: Radial distortion coefficients
            p1, p2: Tangential distortion coefficients
        """
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.p1 = p1
        self.p2 = p2
    
    def distort(self, x: float, y: float) -> tuple:
        """
        Apply distortion to normalized coordinates.
        
        Distortion equations:
        x_d = x(1 + k1*r² + k2*r⁴ + k3*r⁶) + 2*p1*x*y + p2*(r² + 2*x²)
        y_d = y(1 + k1*r² + k2*r⁴ + k3*r⁶) + p1*(r² + 2*y²) + 2*p2*x*y
        
        Args:
            x, y: Undistorted coordinates (centered at 0, normalized)
        
        Returns:
            Tuple of (x_distorted, y_distorted)
        """
        r2 = x*x + y*y
        r4 = r2 * r2
        r6 = r4 * r2
        
        # Radial distortion factor
        radial = 1 + self.k1 * r2 + self.k2 * r4 + self.k3 * r6
        
        # Apply distortion
        x_d = x * radial + 2 * self.p1 * x * y + self.p2 * (r2 + 2 * x * x)
        y_d = y * radial + self.p1 * (r2 + 2 * y * y) + 2 * self.p2 * x * y
        
        return (x_d, y_d)
    
    def undistort(self, x_d: float, y_d: float, iterations: int = 5) -> tuple:
        """
        Remove distortion using iterative Newton-Raphson.
        
        Since the inverse has no closed-form solution, we iterate.
        
        Args:
            x_d, y_d: Distorted coordinates
            iterations: Number of refinement steps
        
        Returns:
            Tuple of (x_undistorted, y_undistorted)
        """
        # Initial guess: distorted = undistorted
        x, y = x_d, y_d
        
        for _ in range(iterations):
            # Compute distortion at current estimate
            x_est, y_est = self.distort(x, y)
            
            # Error
            dx = x_d - x_est
            dy = y_d - y_est
            
            # Update estimate
            x += dx
            y += dy
            
            # Check convergence
            if dx*dx + dy*dy < 1e-12:
                break
        
        return (x, y)
    
    def distort_vector(self, vector: list, center_idx: int = None) -> list:
        """
        Apply distortion to a data vector based on "distance from center."
        
        Elements near center_idx are undistorted (priority).
        Elements far from center are compressed (low priority).
        
        Args:
            vector: Input data vector
            center_idx: Index of attention center (default: middle)
        
        Returns:
            Distorted vector
        """
        import numpy as np
        
        n = len(vector)
        if n == 0:
            return vector
        
        if center_idx is None:
            center_idx = n // 2
        
        result = []
        for i, val in enumerate(vector):
            # Normalized distance from center (-1 to 1)
            dist = (i - center_idx) / max(1, n / 2)
            
            # Apply 1D distortion (radial only)
            r2 = dist * dist
            scale = 1 + self.k1 * r2 + self.k2 * r2 * r2
            
            result.append(val * scale)
        
        return result
    
    @staticmethod
    def attention_distortion(priority: float = 0.5) -> 'DistortionModel':
        """
        Create a distortion model based on attention/priority level.
        
        High priority = more compression at periphery (tunnel vision).
        Low priority = flatter distortion (broad awareness).
        
        Args:
            priority: 0.0 (relaxed) to 1.0 (focused)
        
        Returns:
            Configured DistortionModel
        """
        # Higher priority = more barrel distortion (tunnel vision)
        k1 = priority * 0.3  # Mild barrel when focused
        return DistortionModel(k1=k1, k2=0.0, k3=0.0)


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

