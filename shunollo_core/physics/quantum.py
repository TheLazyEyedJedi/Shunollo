"""
Shunollo Quantum Biology
========================
Implements "Frontier" physics: Quantum effects in sensory transduction.
Derived from:
1. Radical Pair Mechanism (Schulten/Ritz) - Magnetoreception
2. Vibration Theory (Turin) - Olfaction (Tunneling)
"""

import numpy as np
import cmath
from typing import Optional
from .thermo import ThermodynamicSystem, LandauerMonitor, SIM_TEMP_BASELINE

class RadicalPairSensor:
    """
    Simulates a Cryptochrome-based magnetic compass.
    Uses spin dynamics of a Radical Pair to detect weak fields.
    
    Mechanism:
    The Singlet(S) <-> Triplet(T) interconversion yield is modulated 
    by the external magnetic field angle relative to the sensor.
    """
    
    def __init__(self, hyperfine_interaction: float = 1.0, thermo_system: Optional[ThermodynamicSystem] = None):
        self.a_iso = hyperfine_interaction
        self.thermo = thermo_system
    
    def detect_field_alignment(self, field_vector: np.ndarray, sensor_orientation: np.ndarray) -> float:
        """
        Calculate the chemical yield (Singlet fraction) based on field angle.
        
        Args:
            field_vector: 3D vector of the external field (e.g., Signal Gradient)
            sensor_orientation: 3D vector of the sensor (Agent's heading)
            
        Returns:
            Singlet Yield [0.0 - 1.0]. 
            Variations indicate alignment with the field lines.
        """
        # Thermal Decoherence Check
        # If heat is high, quantum states collapse to random mix (0.5 yield)
        if self.thermo:
            T_current = self.thermo.temperature
            # Decoherence threshold: 5 degrees fever (315K) destroys subtle coherence
            if T_current > SIM_TEMP_BASELINE + 5.0:
                 return 0.5

        # Normalize inputs
        B = np.linalg.norm(field_vector)
        if B == 0:
            return 0.5  # No field = Random spin
            
        f_hat = field_vector / B
        s_hat = sensor_orientation / np.linalg.norm(sensor_orientation)
        
        # Angle theta
        cos_theta = np.dot(f_hat, s_hat)
        
        # Simplified spin dynamics approximation (Timmel et al. 2001)
        # Yield is dependent on angle theta (anisotropy)
        # Phi = Phi_0 + Delta * (3 * cos^2(theta) - 1)
        
        # Base yield (isotropic)
        phi_0 = 0.4
        # Anisotropy magnitude (depends on hyperfine coupling)
        delta = 0.1 * self.a_iso
        
        yield_singlet = phi_0 + delta * (3 * (cos_theta**2) - 1)
        
        # Clamp to physical probability range
        return np.clip(yield_singlet, 0.0, 1.0)


class TunnelingSpectrometer:
    """
    Simulates olfactory receptors as Inelastic Electron Tunneling Spectrometers (IETS).
    (Luca Turin's Vibration Theory).
    
    Mechanism:
    Electron tunnels only if phonon energy (h * omega) matches the energy gap (Delta E).
    Detects 'Vibrational Modes' (Frequency) rather than 'Shape'.
    """
    
    def __init__(
        self, 
        energy_gap: float = 1.0, 
        resolution: float = 0.1,
        thermo_system: Optional[ThermodynamicSystem] = None
    ):
        self.delta_E = energy_gap
        self.sigma = resolution  # Line width of the resonance
        self.thermo = thermo_system
    
    def measure_conductance(self, vibrational_frequency: float) -> float:
        """
        Calculate tunneling rate via Fermi's Golden Rule.
        
        Args:
            vibrational_frequency: The frequency mode of the input signal (omega).
            
        Returns:
            Tunneling Current (Conductance) [0.0 - 1.0]
        """
        # Planck's constant (normalized)
        hbar = 1.0 
        
        phonon_energy = hbar * vibrational_frequency
        
        # Resonance condition: Phonon Energy == Energy Gap
        # Modeled as a Gaussian (Lorentzian is also valid)
        mismatch = phonon_energy - self.delta_E
        
        # Tunneling probability
        tunneling = np.exp(- (mismatch**2) / (2 * self.sigma**2))
        
        # Inelastic Tunneling deposits energy into the phonon mode (Heat)
        # 1.0 conductance = 1.0 phonon energy dissipated
        if self.thermo and tunneling > 0.01:
             heat_released = tunneling * 0.1 # Coupling constant
             self.thermo.add_heat(heat_released)
        
        return tunneling

    def analyze_spectrum(self, signal_frequencies: np.ndarray) -> np.ndarray:
        """
        Scan a signal for specific "smells" (frequency modes).
        This simulates a nose with receptors tuned to different gaps.
        """
        # For simplicity, this sensor instance is tuned to ONE gap (self.delta_E).
        # To simulate a full nose, you'd need multiple TunnelingSpectrometer instances.
        
        readings = [self.measure_conductance(f) for f in signal_frequencies]
        return np.array(readings)
