"""
Tests for Phase 14: Integrative Physics (Round 3 Fixes)
Covers: Explicit Units, Thermal Coupling, DDM Urgency
"""
import pytest
import numpy as np
import time
from shunollo_core.physics.constants import SIM_TEMP_BASELINE, LANDAUER_BIT_ENERGY
from shunollo_core.physics.thermo import ThermodynamicSystem, LandauerMonitor
from shunollo_core.physics.quantum import RadicalPairSensor, TunnelingSpectrometer
from shunollo_core.cognition.decision import DriftDiffusionModel

class TestThermodynamics:
    def setup_method(self):
        # DI: Create local system for each test
        self.sys = ThermodynamicSystem() 
        
    def test_temperature_baseline(self):
        """System should start at biological baseline (310K)."""
        assert self.sys.temperature == SIM_TEMP_BASELINE
        
    def test_landauer_heating(self):
        """Erasing bits should generate correct heat (Unit Check)."""
        monitor = LandauerMonitor(system_link=self.sys)
        initial_temp = self.sys.temperature
        
        # Erase 1 bit
        monitor.erase_bits(1)
        
        # Check heat added
        # Heat = LANDAUER_BIT_ENERGY * (T/T_base)
        # Since T approx T_base, added heat approx LANDAUER_BIT_ENERGY
        # dT = Heat / Capacity (1.0)
        expected_rise = LANDAUER_BIT_ENERGY 
        
        current_temp = self.sys.temperature
        rise = current_temp - initial_temp
        
        assert rise > 0
        assert np.isclose(rise, expected_rise, atol=1e-5)
        
    def test_passive_cooling(self):
        """System should cool down over time."""
        self.sys._temperature = 400.0 # Heat it up
        self.sys._last_update = time.time() - 100 
        
        current = self.sys.temperature
        assert current < 400.0
        assert current >= SIM_TEMP_BASELINE


class TestQuantumBiology:
    def setup_method(self):
        self.sys = ThermodynamicSystem()

    def test_thermal_decoherence(self):
        """High temperature should break quantum coherence."""
        sensor = RadicalPairSensor(thermo_system=self.sys)
        field = np.array([0, 0, 1])
        orientation = np.array([0, 0, 1])
        
        # 1. Healthy Temp (310K) -> Yield varies
        self.sys._temperature = SIM_TEMP_BASELINE
        yield_1 = sensor.detect_field_alignment(field, orientation)
        assert yield_1 != 0.5 # Has signal
        
        # 2. Fever Temp (320K) -> Decoherence (0.5 yield)
        self.sys._temperature = SIM_TEMP_BASELINE + 10.0
        yield_2 = sensor.detect_field_alignment(field, orientation)
        
        assert yield_2 == 0.5 # Noise dominated
        
    def test_smell_generates_heat(self):
        """Tunneling events should deposit energy into the system."""
        sensor = TunnelingSpectrometer(thermo_system=self.sys)
        initial_energy = self.sys._entropy_accumulated
        
        # Resonant frequency (hbar=1, gap=1.0)
        sensor.measure_conductance(1.0)
        
        # Should have generated heat
        assert self.sys._entropy_accumulated > initial_energy


class TestDecisionDynamics:
    def test_urgency_accelerates_decision(self):
        """Collapsing bounds should force faster decisions."""
        # Case A: No Urgency (Fixed Bound)
        ddm_slow = DriftDiffusionModel(threshold=2.0, urgency_decay=0.0, noise_level=0.1)
        
        # Case B: High Urgency (Collapsing Bound)
        ddm_fast = DriftDiffusionModel(threshold=2.0, urgency_decay=2.0, noise_level=0.1)
        
        # Use weak drift so it takes time
        drift = 0.5
        
        _, rt_slow = ddm_slow.simulate_trial(drift_rate=drift, max_time=10.0)
        _, rt_fast = ddm_fast.simulate_trial(drift_rate=drift, max_time=10.0)
        
        # Fast DDM should finish sooner because bound drops to meet evidence
        assert rt_fast < rt_slow
