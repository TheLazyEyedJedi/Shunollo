"""
Shunollo Thermodynamics
=======================
Implements the "Thermodynamic Floor" of cognition.
Focuses on Landauer's Principle, Entropy Production, and System Temperature.
"""

import math
import time
from typing import Dict, Optional
from .constants import SIM_BOLTZMANN, SIM_TEMP_BASELINE, LANDAUER_BIT_ENERGY


class ThermodynamicSystem:
    """
    Global thermodynamic state of the cognitive system.
    Tracks 'System Temperature' which rises with computation (erasure)
    and decays with cooling (rest).
    """
    
    def __init__(self, baseline_temp: float = SIM_TEMP_BASELINE):
        self._temperature = baseline_temp
        self._entropy_accumulated = 0.0
        self._last_update = time.time()
        self.cooling_rate = 10.0  # Kelvin per second
    
    @property
    def temperature(self) -> float:
        """Current system temperature in Kelvin."""
        self._update_cooling()
        return self._temperature
    
    def _update_cooling(self):
        """Apply passive cooling using Newton's Law of Cooling."""
        now = time.time()
        dt = now - self._last_update
        if dt > 0:
            # Newton's Law: dT/dt = -k(T - T_env)
            # Higher T - T_env leads to faster absolute cooling
            delta = self._temperature - SIM_TEMP_BASELINE
            if abs(delta) > 1e-6:
                # Use a more stable exponential decay based on cooling_rate
                # self.cooling_rate Kelvin/sec is our target at high gradients
                k = self.cooling_rate / (delta + 1e-6) if delta > 0 else 0.1
                # Simplified: self.cooling_rate acts as a gain
                decay = math.exp(-0.01 * self.cooling_rate * dt)
                self._temperature = SIM_TEMP_BASELINE + delta * decay
            self._last_update = now

    def add_heat(self, joules: float):
        """Inject heat into the system (e.g., from Erasure)."""
        self._update_cooling()
        # Simplified heat capacity model: C = 1.0 (Simulation Units)
        # dT = dQ / C
        self._temperature += joules
        self._entropy_accumulated += joules / self._temperature
        
    def reset(self):
        """Reset to biological baseline."""
        self._temperature = SIM_TEMP_BASELINE
        self._entropy_accumulated = 0.0
        self._last_update = time.time()


class LandauerMonitor:
    """
    Monitors information erasure events and generates corresponding heat.
    E >= kB * T * ln(2)
    """
    
    def __init__(self, system_link: Optional[ThermodynamicSystem] = None):
        """
        Args:
            system_link: The thermodynamic system to heat up.
                         If None, creates a local private system (functional but isolated).
        """
        self.system = system_link if system_link else ThermodynamicSystem()
        
    def erase_bits(self, num_bits: int):
        """
        Record the erasure of 'num_bits'.
        Generates heat proportional to the Landauer Limit.
        """
        if num_bits <= 0:
            return
            
        # Optimization: Use pre-calculated constant
        # Note: Strictly Landauer energy is T-dependent (E = kB * T * ln2)
        # We use current T to calculate energy cost.
        
        current_temp = self.system.temperature
        
        # Scaling adjustment: LANDAUER_BIT_ENERGY in constants.py is calculated at BASELINE (310K).
        # We must scale it by (T / T_baseline) to be physically accurate.
        
        energy_factor = current_temp / SIM_TEMP_BASELINE
        heat_generated = num_bits * LANDAUER_BIT_ENERGY * energy_factor
        
        # Apply heat
        self.system.add_heat(heat_generated)
        
    def get_noise_floor(self) -> float:
        """
        Return the thermal noise floor (Johnson-Nyquist).
        Noise Power P = 4 * kB * T * B (bandwidth assumed 1)
        Returns sqrt(P) -> Amplitude
        """
        temp = self.system.temperature
        # Noise amplitude scales with sqrt(T)
        return math.sqrt(SIM_BOLTZMANN * temp)


def carnot_efficiency(t_hot: float, t_cold: float = 310.0) -> float:
    """
    Calculate theoretical maximum efficiency of a heat engine.
    eta = 1 - (Tc / Th)
    """
    if t_hot <= t_cold:
        return 0.0
    return 1.0 - (t_cold / t_hot)


# ==============================================================================
# TEMPERATURE KINETICS (Arrhenius)
# ==============================================================================

class ThermoDynamics:
    """
    Temperature-dependent kinetics using Arrhenius equation.
    Models how reaction rates (and failure rates) depend exponentially
    on temperature via activation energy barriers.
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
        """
        import math
        
        delta = temperature_celsius - threshold_celsius
        
        # Sigmoid centered at threshold
        try:
            return 1.0 / (1.0 + math.exp(-sensitivity * delta))
        except OverflowError:
            return 1.0 if delta > 0 else 0.0
