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
        """Apply passive cooling over time."""
        now = time.time()
        dt = now - self._last_update
        if dt > 0:
            # Newton's Law of Cooling
            delta = self._temperature - SIM_TEMP_BASELINE
            decay = math.exp(-0.1 * dt)
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
