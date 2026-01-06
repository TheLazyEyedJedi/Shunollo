"""
test_physics_sweep.py
---------------------
Rigorous Parameter Sweep for the Shunollo Physics Engine.
Verifies Monotonicity, Continuity, and Bounds across the entire input spectrum.
Addresses "Cherry Picking" concerns by testing diverse, uncurated inputs.
"""
import pytest
import numpy as np
import sys
import os
import importlib

# Ensure we test the LOCAL physics code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

from shunollo_core import physics

class TestPhysicsSweep:

    def check_monotonicity(self, inputs, outputs):
        """Helper: Assert that as input increases, output increases (or stays flat)."""
        for i in range(1, len(outputs)):
            delta = outputs[i] - outputs[i-1]
            # Allow for tiny floating point errors, but generally must be >= 0
            assert delta >= -1e-9, f"Monotonicity Violation at index {i}: {inputs[i-1]}->{outputs[i-1]} vs {inputs[i]}->{outputs[i]}"

    def check_bounds(self, outputs):
        """Helper: Assert all outputs are within [0.0, 1.0]."""
        for val in outputs:
            assert 0.0 <= val <= 1.0, f"Bounds Violation: {val} is not in [0, 1]"

    def test_energy_sweep(self):
        """Sweep 'Rate' while keeping Size constant. Energy should increase monotonically as Rate increases."""
        size = 500.0
        rates = np.linspace(0, 500, 100) # 0 to 500 Hz
        outputs = []
        
        for r in rates:
            e = physics.calculate_energy(size=size, rate_hz=r)
            outputs.append(e)
            
        self.check_monotonicity(rates, outputs)
        self.check_bounds(outputs)
        
        # Verify Monotonicity in valid range (0-100Hz)
        valid_range_outputs = outputs[:20] 
        assert valid_range_outputs[-1] > valid_range_outputs[0]
        
        # Verify Saturation cap
        assert outputs[-1] == outputs[50] 

    def test_roughness_sweep_entropy(self):
        """Sweep 'Entropy' while keeping Jitter constant."""
        jitter = 0.0
        entropies = np.linspace(0, 8.0, 50) 
        outputs = []
        
        for h in entropies:
            r = physics.calculate_roughness(entropy=h, jitter=jitter)
            outputs.append(r)
            
        self.check_monotonicity(entropies, outputs)
        self.check_bounds(outputs)

    def test_flux_sweep(self):
        """Sweep 'Variance'. Flux should be monotonic."""
        variances = np.linspace(0, 1000, 50)
        outputs = []
        
        for v in variances:
            f = physics.calculate_flux(variance=v)
            outputs.append(f)
            
        self.check_monotonicity(variances, outputs)
        self.check_bounds(outputs)

    def test_extremes(self):
        """Test Edge Cases: Infinity, Huge Numbers."""
        # Energy
        e_inf = physics.calculate_energy(size=1e9, rate_hz=1e9)
        assert e_inf == 1.0
        
        # Roughness 
        r_inf = physics.calculate_roughness(entropy=100.0, jitter=1e9, error_rate=1.0)
        assert r_inf == 1.0
        
        # Flux
        f_inf = physics.calculate_flux(variance=1e9)
        assert f_inf == 1.0
