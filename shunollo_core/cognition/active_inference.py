"""
Active Inference Agent
----------------------
Variational free energy minimization for autonomous agents based on
Karl Friston's Free Energy Principle.

Mathematical Foundation:
    Variational Free Energy: F = Accuracy + Complexity
    Accuracy: (1/2)(y - g(μ))ᵀ Π_z (y - g(μ))
    Complexity: (1/2) ln(Π_z / Π_μ)
    Action Selection: a* = argmin_a E[F | a] (via Drift Diffusion)
"""
import numpy as np
from typing import Dict, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
import logging
import threading

from shunollo_core.brain.autoencoder import get_imagination
from shunollo_core.physics.thermo import ThermodynamicSystem
from shunollo_core.cognition.decision import DriftDiffusionModel

__all__ = [
    'InferenceState',
    'ActiveInferenceAgent',
    'create_active_inference_agent',
]

logger = logging.getLogger(__name__)


@dataclass
class InferenceState:
    """Result of an active inference loop iteration."""
    free_energy: float
    accuracy: float
    complexity: float
    precision: float
    action_taken: Optional[str]
    converged: bool
    iterations: int
    errors: List[str] = field(default_factory=list)


class ActiveInferenceAgent:
    """
    Variational free energy minimization agent.
    
    Implements the perception-action loop where agents minimize surprise by
    updating beliefs or acting on the environment.
    """
    
    DEFAULT_INPUT_SIZE = 13
    MIN_PRECISION = 0.1
    MAX_PRECISION = 10.0
    MAX_HISTORY_SIZE = 100
    
    __slots__ = (
        'imagination', 'motor_registry', 'eta', 'max_iterations',
        'threshold', 'precision', 'prior_precision', 'input_size',
        'memory_system', 'thermo_system', 'ddm', 'metabolic_cost', 
        'fatigue_rate', 'refractory_period', 'last_action_time',
        '_action_history', '_lock'
    )
    
    def __init__(
        self,
        imagination: Optional[object] = None,
        motor_registry: Optional[Dict[str, Callable]] = None,
        memory_system: Optional[object] = None,
        thermo_system: Optional[ThermodynamicSystem] = None,
        learning_rate: float = 0.1,
        max_iterations: int = 3,
        convergence_threshold: float = 0.1,
        prior_precision: float = 1.0,
        input_size: Optional[int] = None,
        fatigue_rate: float = 0.01
    ) -> None:
        """
        Initialize the agent.
        
        Args:
            imagination: Autoencoder for predictions
            motor_registry: Dict mapping action names to callables
            memory_system: FactorGraph or similar for episodic memory
            thermo_system: ThermodynamicSystem
            learning_rate: η for gradient updates
            max_iterations: Maximum perception-action cycles
            convergence_threshold: F below this = converged
            prior_precision: Prior belief about precision (Π_μ)
            input_size: Override autoencoder input size
            fatigue_rate: Cost per inference cycle (Metabolic Cost)
        """
        self.imagination = imagination or get_imagination()
        self.motor_registry = motor_registry or {}
        self.memory_system = memory_system
        self.thermo_system = thermo_system
        
        # Decision Dynamics
        # Urgency 0.5 allows bounds to collapse over ~2 seconds
        self.ddm = DriftDiffusionModel(threshold=2.0, urgency_decay=0.5)
        
        self.eta = learning_rate
        self.max_iterations = max_iterations
        self.threshold = convergence_threshold
        self.precision = 1.0
        self.prior_precision = prior_precision
        self.fatigue_rate = fatigue_rate
        self.metabolic_cost = 0.0
        self.refractory_period = 0.5 # 500ms between actions
        self.last_action_time = 0.0
        
        if input_size is not None:
            self.input_size = input_size
        elif hasattr(self.imagination, 'input_size'):
            self.input_size = self.imagination.input_size
        else:
            self.input_size = self.DEFAULT_INPUT_SIZE
        
        self._action_history: List[Dict] = []
        self._lock = threading.Lock()
    
    def __repr__(self) -> str:
        temp = f"{self.thermo_system.temperature:.1f}K" if self.thermo_system else "N/A"
        return (
            f"ActiveInferenceAgent(precision={self.precision:.3f}, "
            f"fatigue={self.metabolic_cost:.3f}, "
            f"temp={temp}, "
            f"memory={'Linked' if self.memory_system else 'None'})"
        )
    
    def sleep(self, duration_cycles: int = 10) -> float:
        """Enter sleep mode to consolidate memory and cool down."""
        # 1. Recover from fatigue (Metabolic Restoration)
        restoration = 1.0 - np.exp(-0.1 * duration_cycles)
        self.metabolic_cost *= (1.0 - restoration)
        
        # 2. Consolidate Memory
        consolidation_score = 0.0
        if self.memory_system and hasattr(self.memory_system, 'optimize'):
            try:
                final_energy = self.memory_system.optimize(iterations=duration_cycles)
                consolidation_score = 1.0 / (final_energy + 1e-6)
                logger.debug(f"Sleep consolidation complete. Energy: {final_energy:.4f}")
            except Exception as e:
                logger.error(f"Sleep consolidation failed: {e}")
        
        # 3. Thermodynamic Cooling
        if self.thermo_system:
             # Fast forward cooling by simulating time passed
             # Each sleep cycle represents roughly 0.1s of rest cooling
             self.thermo_system.reset() # Reset to baseline behavior for deep sleep

        # 4. Reset Precision Baseline (Dopamine Reset)
        self.prior_precision = 1.0
        return consolidation_score

    def calculate_free_energy(
        self, observation: np.ndarray, prediction: np.ndarray
    ) -> Tuple[float, float, float]:
        """Calculate variatonal free energy F = Accuracy + Complexity."""
        min_len = min(len(observation), len(prediction))
        y, g_mu = observation[:min_len], prediction[:min_len]
        
        error = y - g_mu
        accuracy = 0.5 * self.precision * np.dot(error, error)
        
        if self.prior_precision > 0:
            complexity = 0.5 * np.log(self.precision / self.prior_precision)
        else:
            complexity = 0.0
        
        return accuracy + complexity, accuracy, complexity
    
    def _estimate_action_gradient(self, action: str, current_f: float) -> float:
        """Estimate action gradient using finite differences on history."""
        with self._lock:
            previous_entries = [h for h in self._action_history if h.get("action") == action]
        if not previous_entries: return 0.0
        previous_f = previous_entries[-1].get("free_energy", current_f)
        # Positive gradient = F increased (Bad). Negative = F decreased (Good).
        return current_f - previous_f
    
    def select_action(
        self, current_free_energy: float, available_actions: List[str]
    ) -> Optional[str]:
        """
        Select action using Drift Diffusion Model (DDM).
        Replaces simple argmax with stochastic accumulation + urgency.
        """
        import time
        now = time.time()
        if not available_actions or current_free_energy < self.threshold:
            return None
        
        # 0. Refractory Period Check
        if now - self.last_action_time < self.refractory_period:
            return None
        
        # 1. Identify best candidate and its gradient
        # We want to minimize F, so we seek negative gradients (improvements)
        candidates = []
        for action in available_actions:
             grad = self._estimate_action_gradient(action, current_free_energy)
             # Signal strength: How much did this action help before?
             # Negative gradient = Help. Positive = Hurt.
             # Invert sign so positive 'drift' means "Good Action"
             drift_signal = -grad 
             candidates.append((action, drift_signal))
        
        # Sort by signal strength (best first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_action, best_drift = candidates[0]
        
        # 2. Race Model Simulation
        # Even if best_drift is small, urgency might force a choice.
        # Scale drift: Small F changes need to drive DDM.
        # Arbitrary scaling factor for simulation robustness
        drift_rate = best_drift * 10.0 
        
        # Clamp drift somewhat to avoid instant bounds if massive error
        drift_rate = max(-5.0, min(5.0, drift_rate))
        
        # 3. Simulate Trial
        # If drift is positive (action helps), we drift to +Threshold (Do It)
        # If drift is negative (action hurts), we drift to -Threshold (Rejection)
        # If 0 (unknown), we drift randomly.
        
        choice, reaction_time = self.ddm.simulate_trial(drift_rate=drift_rate)
        
        if choice == 1:
            # Positive boundary crossed: "Commit to Action"
            return best_action
        elif choice == -1:
            # Negative boundary crossed: "Reject Action" -> Maybe try second best?
            # For simplicity, we just return nothing (Hesitation)
            return None
        else:
            # Timeout (Urgency failed to force choice in time) -> Hesitation
            return None
    
    def minimize_surprise(
        self, signal: np.ndarray, available_actions: Optional[List[str]] = None
    ) -> InferenceState:
        """execute active inference loop."""
        if available_actions is None:
            available_actions = list(self.motor_registry.keys())
        
        if len(signal) < self.input_size:
            raise ValueError(f"Signal length {len(signal)} < required input size {self.input_size}")
        
        # Apply Fatigue (Thermodynamic constraint)
        effective_precision = self.precision / (1.0 + self.metabolic_cost)
        original_precision = self.precision
        self.precision = effective_precision
        
        current_signal = signal.copy()
        action_taken = None
        free_energy = float('inf')
        accuracy, complexity = 0.0, 0.0
        errors: List[str] = []
        
        for iteration in range(self.max_iterations):
            # 1. Metabolism & Heat
            self.metabolic_cost += self.fatigue_rate
            if self.thermo_system:
                # Landauer Cost + Joule Heating from effort
                # Small baseline + proportional to iteration effort
                heat_j = 1e-6 + (self.metabolic_cost * 1e-5)
                self.thermo_system.add_heat(heat_j)
            
            # 2. Perception (VFE)
            try:
                reconstruction, _ = self.imagination.forward(current_signal[:self.input_size])
                g_mu = reconstruction.flatten()
            except Exception as e:
                errors.append(f"Prediction error: {e}")
                break
            
            y_tilde = current_signal.flatten()[:self.input_size]
            free_energy, accuracy, complexity = self.calculate_free_energy(y_tilde, g_mu)
            
            # 3. Convergence Check
            if free_energy < self.threshold:
                self.precision = original_precision
                return InferenceState(free_energy, accuracy, complexity, self.precision, 
                                    action_taken, True, iteration + 1, errors)
            
            # 4. Action Selection (DDM)
            action = self.select_action(free_energy, available_actions)
            
            if action and action in self.motor_registry:
                with self._lock:
                    self._action_history.append({
                        "action": action, "free_energy": free_energy, "iteration": iteration
                    })
                try:
                    self.motor_registry[action]()
                    action_taken = action
                    import time
                    self.last_action_time = time.time()
                except Exception as e:
                    errors.append(f"Action '{action}' failed: {e}")
            
            # 5. Dopamine Update (Precision)
            prediction_error = np.mean(np.abs(y_tilde - g_mu))
            new_precision = 1.0 / (prediction_error + 0.1)
            original_precision = np.clip(new_precision, self.MIN_PRECISION, self.MAX_PRECISION)
            self.precision = original_precision / (1.0 + self.metabolic_cost)
            
            with self._lock:
                if len(self._action_history) > self.MAX_HISTORY_SIZE:
                    self._action_history = self._action_history[-self.MAX_HISTORY_SIZE // 2:]
        
        self.precision = original_precision
        return InferenceState(free_energy, accuracy, complexity, self.precision, 
                            action_taken, False, self.max_iterations, errors)

    def register_action(self, name: str, action: Callable) -> None:
        self.motor_registry[name] = action
    
    def set_precision(self, precision: float) -> None:
        self.precision = np.clip(precision, self.MIN_PRECISION, self.MAX_PRECISION)
    
    def reset(self) -> None:
        self.precision = 1.0
        self.metabolic_cost = 0.0
        with self._lock: self._action_history.clear()


def create_active_inference_agent(
    imagination: Optional[object] = None,
    motor_registry: Optional[Dict[str, Callable]] = None,
    memory_system: Optional[object] = None,
    thermo_system: Optional[ThermodynamicSystem] = None, 
    learning_rate: float = 0.1,
    prior_precision: float = 1.0
) -> ActiveInferenceAgent:
    """Create an ActiveInferenceAgent instance."""
    return ActiveInferenceAgent(
        imagination=imagination,
        motor_registry=motor_registry,
        memory_system=memory_system,
        thermo_system=thermo_system,
        learning_rate=learning_rate,
        prior_precision=prior_precision
    )
