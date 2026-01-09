"""
Shunollo Classical Mechanics
============================
Biomimetic mechanics for signal processing.
Handles Energy, Entropy, Viscosity, and Mechanoreception.
"""
import math
import numpy as np
from typing import List, Tuple

class PhysicsConfig:
    """Tunable constants for the Physics Engine."""
    # Optimization Result (F1=1.0): Entropy=0.7, Jitter=0.1
    ROUGHNESS_ENTROPY_WEIGHT = 0.7
    ROUGHNESS_JITTER_WEIGHT = 0.1
    ROUGHNESS_ERROR_WEIGHT = 0.2
    
    # Statistical Baselines
    BASELINE_JITTER_MAX = 1.0   # 1000ms
    BASELINE_MTU = 1500.0       # Standard Ethernet
    BASELINE_ENTROPY_MAX = 8.0  # Max Shannon Entropy

def calculate_entropy(data: bytes | list | np.ndarray) -> float:
    """Shannon Entropy (Information Density)."""
    if data is None: return 0.0
    if isinstance(data, (bytes, bytearray)):
        arr = np.frombuffer(data, dtype=np.uint8)
    else:
        arr = np.array(data)
    if arr.size == 0: return 0.0
    _, counts = np.unique(arr, return_counts=True)
    probs = counts / arr.size
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)

def calculate_energy(size: float | np.ndarray, rate_hz: float = 0.0, criticality: float = 1.0) -> float | np.ndarray:
    """Multivariate Energy: Size * Rate^1.5 * Criticality."""
    safe_size = np.clip(size, 1, 1500.0)
    norm_size = np.log10(safe_size) / math.log10(1500.0)
    norm_rate = np.clip(rate_hz / 100.0, 0, 1.0)
    raw_energy = (norm_size * (norm_rate ** 1.5))
    return np.clip(raw_energy * criticality, 0.01, 1.0)

def calculate_roughness(entropy: float | np.ndarray, jitter: float = 0.0, error_rate: float = 0.0) -> float | np.ndarray:
    """Multivariate Roughness: Entropy + Jitter + Errors."""
    norm_entropy = np.clip(entropy / PhysicsConfig.BASELINE_ENTROPY_MAX, 0, 1.0)
    norm_jitter = np.clip(jitter / PhysicsConfig.BASELINE_JITTER_MAX, 0, 1.0)
    norm_error = np.clip(error_rate, 0, 1.0)
    roughness = (
        (norm_entropy * PhysicsConfig.ROUGHNESS_ENTROPY_WEIGHT) + 
        (norm_jitter * PhysicsConfig.ROUGHNESS_JITTER_WEIGHT) + 
        (norm_error * PhysicsConfig.ROUGHNESS_ERROR_WEIGHT)
    )
    return np.clip(roughness, 0.0, 1.0)

def calculate_viscosity(delay_ms: float, pressure_psi: int = 0) -> float:
    """Multivariate Viscosity: Delay + Load."""
    norm_delay = min(1.0, delay_ms / 2000.0)
    norm_pressure = min(1.0, pressure_psi / 100.0)
    viscosity = norm_delay + (norm_pressure * 0.5)
    return min(1.0, viscosity)

def calculate_harmony(entropy: float, protocol_valid: bool, port_standard: bool, expected_high_entropy: bool = False) -> float:
    """Multivariate Harmony: Structure + Expectation."""
    score = 1.0
    if not protocol_valid: score -= 0.5
    if not port_standard: score -= 0.2
    if entropy > 7.0 and protocol_valid and not expected_high_entropy: score -= 0.8
    return max(0.0, score)

def calculate_flux(variance: float, limit: float = 100.0) -> float:
    """Flux: Rate of Change / Jitter."""
    return min(1.0, variance / limit)

# ==============================================================================
# SENSORY CLASSES
# ==============================================================================

class Somatosensory:
    """The Sense of Touch (Texture, Vibration, Temperature)."""
    @staticmethod
    def calculate_texture(entropy: float) -> float: return min(1.0, entropy / 8.0)
    @staticmethod
    def calculate_vibration(jitter_ms: float) -> float: return min(1.0, jitter_ms / 100.0)
    @staticmethod
    def calculate_temperature(flux: float) -> float: return min(1.0, flux * 2.0)

class Proprioception:
    """The Sense of Body Position (Strain, Tension, Load)."""
    @staticmethod
    def calculate_strain(load_factor: float) -> float: return min(1.0, load_factor)
    @staticmethod
    def calculate_tension(pressure_psi: float) -> float: return min(1.0, pressure_psi)

class Vestibular:
    """The Sense of Balance (Stability, Acceleration)."""
    @staticmethod
    def calculate_vertigo(stability_loss: float) -> float: return min(1.0, stability_loss * 5.0) 
    @staticmethod
    def calculate_acceleration(velocity_delta: float) -> float: return min(1.0, velocity_delta)

class Nociception:
    """The Sense of Pain (Damage, Stress)."""
    @staticmethod
    def calculate_pain(trauma_level: float, stress_duration: float) -> float:
        structural_pain = min(1.0, trauma_level * 2.0)
        thermal_pain = min(1.0, stress_duration)
        return max(structural_pain, thermal_pain)

class VestibularDynamics:
    """Steinhausen torsion pendulum model for integration."""
    def __init__(self, damping: float = 0.85, time_constant: float = 10.0):
        self.damping = damping
        self.time_constant = time_constant
        self._velocity = 0.0
        self._history: List[float] = []
    
    def integrate_acceleration(self, acceleration: float) -> float:
        self._velocity = self.damping * self._velocity + (1 - self.damping) * acceleration
        self._history.append(self._velocity)
        if len(self._history) > 100: self._history = self._history[-100:]
        return self._velocity
    
    def get_cumulative_displacement(self) -> float:
        if not self._history: return 0.0
        return sum(self._history) / len(self._history)
    
    def reset(self):
        self._velocity = 0.0
        self._history.clear()

class StressTensor:
    """Von Mises stress for detecting distortion."""
    @staticmethod
    def calculate_von_mises(sigma_1: float, sigma_2: float, sigma_3: float = 0.0) -> float:
        term1 = (sigma_1 - sigma_2) ** 2
        term2 = (sigma_2 - sigma_3) ** 2
        term3 = (sigma_3 - sigma_1) ** 2
        return math.sqrt(0.5 * (term1 + term2 + term3))
    
    @staticmethod
    def is_distortion_anomaly(stresses: list, uniform_threshold: float = 0.1) -> Tuple[bool, float, float]:
        if len(stresses) < 2: return False, 0.0, stresses[0] if stresses else 0.0
        s = list(stresses[:3]) + [0.0] * (3 - len(stresses))
        von_mises = StressTensor.calculate_von_mises(s[0], s[1], s[2])
        mean_pressure = sum(s) / len(s)
        if mean_pressure > 0:
            relative_distortion = von_mises / mean_pressure
        else:
            relative_distortion = von_mises
        return relative_distortion > uniform_threshold, von_mises, mean_pressure

# ==============================================================================
# BIOPHYSICS & ADVANCED MECHANICS
# ==============================================================================

class ChemicalKinetics:
    """Chemical binding kinetics for saturation and concentration modeling."""
    @staticmethod
    def hill_langmuir(concentration: float, kd: float = 0.5, hill_coefficient: float = 1.0) -> float:
        if concentration <= 0 or kd <= 0: return 0.0
        c_n = concentration ** hill_coefficient
        kd_n = kd ** hill_coefficient
        return c_n / (kd_n + c_n)
    
    @staticmethod
    def nernst_potential(concentration_inside: float, concentration_outside: float, valence: int = 1, temperature_kelvin: float = 310.0) -> float:
        if concentration_inside <= 0 or concentration_outside <= 0: return 0.0
        R, F = 8.314, 96485
        return (1000 * R * temperature_kelvin / (valence * F)) * math.log(concentration_outside / concentration_inside)
    
    @staticmethod
    def binding_rate(concentration: float, k_on: float = 1.0, k_off: float = 0.1) -> float:
        if k_on <= 0: return 0.0
        forward = k_on * concentration
        return forward / (forward + k_off)

class MechanoFilter:
    """Viscoelastic mechanical filtering (Pacinian Corpuscle)."""
    def __init__(self, time_constant: float = 0.05):
        self.tau = time_constant
        self._prev_input = 0.0
        self._prev_output = 0.0
    
    def filter(self, input_value: float, dt: float = 0.01) -> float:
        if dt <= 0: dt = 0.01
        alpha = self.tau / (self.tau + dt)
        output = alpha * (self._prev_output + input_value - self._prev_input)
        self._prev_input = input_value
        self._prev_output = output
        return output
    
    def reset(self):
        self._prev_input = 0.0
        self._prev_output = 0.0
    
    @staticmethod
    def adaptation_time_constant(capsule_layers: int = 30, fluid_viscosity: float = 1.0) -> float:
        return 0.002 * capsule_layers * fluid_viscosity

class CriticalResonator:
    """Hopf Bifurcation model for active amplification (Cochlear)."""
    def __init__(self, natural_frequency: float = 1.0, damping: float = 0.01, nonlinear_coefficient: float = 1.0):
        self.omega0 = natural_frequency
        self.zeta = damping
        self.beta = nonlinear_coefficient
    
    def gain(self, input_amplitude: float) -> float:
        if input_amplitude <= 0: return 0.0
        linear_gain = 1.0 / (2.0 * self.zeta) if self.zeta > 0 else 100.0
        crossover = self.zeta / self.beta if self.beta > 0 else 1.0
        if input_amplitude < crossover: return linear_gain
        return linear_gain * (crossover / input_amplitude) ** (2.0 / 3.0)
    
    def amplify(self, input_signal: float) -> float:
        return input_signal * self.gain(abs(input_signal))
    
    def sensitivity_enhancement(self) -> float:
        if self.zeta <= 0: return 60.0
        enhancement_db = 20.0 * math.log10(1.0 / (2.0 * self.zeta))
        return min(60.0, max(0.0, enhancement_db))
    
    def is_near_bifurcation(self) -> bool:
        return self.zeta < 0.1

# ==============================================================================
# HIGH-LEVEL METRICS (Phase 280)
# ==============================================================================

def calculate_dissonance(energy: float, saturation: float, harmony: float) -> float:
    """Multivariate Dissonance (Tone Tension)."""
    discord = (1.0 - harmony) * energy
    return max(0.0, min(discord * saturation, 1.0))

def calculate_ewr(entropy: float, wait_ms: float) -> float:
    """Entropy-to-Wait Ratio (EWR)."""
    if wait_ms <= 0: return 1.0
    return entropy / (wait_ms + 1.0)

def calculate_action_potential(kinetic: float, potential: float) -> float:
    """Lagrangian Mechanics (Principle of Least Action)."""
    norm_t = min(1.0, kinetic / 1000.0)
    norm_v = min(1.0, potential / 500.0)
    lagrangian = norm_t - norm_v
    return 1.0 - max(0.0, min(1.0, (lagrangian + 1.0) / 2.0))

def calculate_hamiltonian(kinetic: float, potential: float) -> float:
    """Hamiltonian Energy (H = T + V)."""
    norm_t = min(1.0, kinetic / 1000.0)
    norm_v = min(1.0, potential / 500.0)
    return (norm_t + norm_v) / 2.0

def vectorize_sensation(physics_dict: dict, protocol: str = "tcp") -> list:
    """Convert a physics dictionary into a 13-dimensional Somatic Vector."""
    def g(key, default=0.0):
        return max(0.0, min(1.0, float(physics_dict.get(key, default))))
    
    proto = protocol.lower()
    is_tcp = 1.0 if proto == "tcp" else 0.0
    is_udp = 1.0 if proto == "udp" else 0.0
    is_other = 1.0 if (not is_tcp and not is_udp) else 0.0
    
    return [
        g("roughness"), g("flux"), g("viscosity"), g("salience"),
        g("dissonance"), g("volatility"), g("action"), g("hamiltonian"),
        g("ewr"), g("harmony", 1.0), is_tcp, is_udp, is_other
    ]
