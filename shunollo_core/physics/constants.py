"""
Shunollo Physics Constants
==========================
Defines the physical constants and unit scaling system.
This file serves as the "Ground Truth" for dimensional consistency.

The simulation uses a "Mesoscopic Unit System" where energy is scaled 
to be perceptible in signal processing terms (e.g., standard deviations),
rather than using raw SI units which would result in negligible 1e-23 values.
"""

# Natural Constants (SI)
REAL_BOLTZMANN = 1.380649e-23  # J/K
REAL_PLANCK = 6.62607015e-34   # J*s
REAL_TEMP_BODY = 310.15        # K (37 C)

# Simulation Constants (Mesoscopic Scaling)
# Scale Factor: 1.0 SimJoules approx 1e-21 RealJoules (ATP scale)
# This acts as a normalization to allow float32/64 stability.

SIM_BOLTZMANN = 0.01  # Simulation Units per Kelvin
SIM_PLANCK = 1.0      # Normalization for Quantum Action (hbar=1)
SIM_TEMP_BASELINE = 310.0 # Baseline Temperature (K)

# Landauer Limit (Simulation Units)
# E = kB * T * ln(2)
# At 310K: 0.01 * 310 * 0.693 = 2.14 SimJoules per bit
LANDAUER_BIT_ENERGY = SIM_BOLTZMANN * SIM_TEMP_BASELINE * 0.69314718056

# Metabolic Constants
# Energy (SimJoules) per ATP hydrolysis equivalent
ATP_ENERGY = 20.0 * SIM_BOLTZMANN * SIM_TEMP_BASELINE # ~600 SimJoules
