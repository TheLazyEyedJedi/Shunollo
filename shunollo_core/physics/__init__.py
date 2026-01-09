"""
Shunollo Physics Engine
=======================
The unified physics package for the Isomorphic Architecture.
Handles Thermodynamics, Quantum Mechanics, Classical Mechanics, Optics, and Networks.
"""

from .mechanics import (
    PhysicsConfig, calculate_entropy, calculate_energy, calculate_roughness,
    calculate_viscosity, calculate_harmony, calculate_flux,
    Somatosensory, Proprioception, Vestibular, Nociception,
    VestibularDynamics, StressTensor, ChemicalKinetics, MechanoFilter,
    CriticalResonator, calculate_dissonance, calculate_ewr,
    calculate_action_potential, calculate_hamiltonian, vectorize_sensation
)

from .thermo import (
    ThermodynamicSystem, LandauerMonitor, carnot_efficiency, ThermoDynamics
)

from .quantum import (
    RadicalPairSensor, TunnelingSpectrometer
)

from .optics import (
    Psychophysics, DistortionModel, NoisePhysics
)

from .network import (
    PropagationPhysics, ImpedanceAnalyzer, calculate_manifold_distance
)

from .time_series import (
    PoissonDetector, calculate_volatility_index, calculate_lyapunov_exponent
)

from .graph import (
    FactorGraph
)

from .constants import (
    SIM_BOLTZMANN, SIM_TEMP_BASELINE, LANDAUER_BIT_ENERGY
)
