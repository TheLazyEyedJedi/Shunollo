"""
Shunollo Decision Dynamics
==========================
Implements Drift Diffusion Models (DDM) for stochastic decision making.
Replaces instantaneous "max logic" with time-dependent evidence accumulation.
"""

import numpy as np
from typing import Optional, Tuple

class DriftDiffusionModel:
    """
    Simulates decision making as a particle diffusing towards a boundary.
    Equation: dx = v * dt + sigma * dW
    
    Attributes:
        threshold (float): The boundary (+/- a) for making a decision.
        noise_level (float): The diffusion coefficient (sigma).
        non_decision_time (float): Sensory/Motor latency (T_er).
    """

    def __init__(
        self, 
        threshold: float = 1.0, 
        noise_level: float = 0.1,
        non_decision_time: float = 0.1,
        urgency_decay: float = 0.0
    ):
        self.initial_threshold = threshold
        self.noise_level = noise_level
        self.non_decision_time = non_decision_time
        self.urgency_decay = urgency_decay # Lambda for collapsing bound
        
        # Internal state
        self.evidence = 0.0
        self.time_elapsed = 0.0
        
    def reset(self):
        """Reset the accumulator."""
        self.evidence = 0.0
        self.time_elapsed = 0.0

    def step(self, drift_rate: float, dt: float = 0.01) -> Optional[int]:
        """
        Advance the decision process by one time step.
        """
        self.time_elapsed += dt
        
        # Wiener process increment (Gaussian white noise * sqrt(dt))
        dW = np.random.normal(0, np.sqrt(dt))
        
        # Stochastic Differential Equation
        dx = (drift_rate * dt) + (self.noise_level * dW)
        
        self.evidence += dx
        
        # Calculate dynamic threshold (Urgency)
        # Threshold(t) = T_0 * exp(-lambda * t)
        if self.urgency_decay > 0:
            current_threshold = self.initial_threshold * np.exp(-self.urgency_decay * self.time_elapsed)
            # Prevent threshold crossing 0 (absurdity check)
            current_threshold = max(0.1, current_threshold)
        else:
            current_threshold = self.initial_threshold
        
        # Check boundaries
        if self.evidence >= current_threshold:
            return 1
        elif self.evidence <= -current_threshold:
            return -1
            
        return None
        
    def simulate_trial(self, drift_rate: float, max_time: float = 2.0) -> Tuple[int, float]:
        """
        Run a full simulation until decision or timeout.
        
        Returns:
            (Choice, ReactionTime)
            Choice is 0 if timed out.
        """
        self.reset()
        t = 0.0
        dt = 0.01
        
        while t < max_time:
            choice = self.step(drift_rate, dt)
            if choice is not None:
                return choice, t + self.non_decision_time
            t += dt
            
        return 0, max_time  # Timeout

class BayesianDriftModel:
    """
    Extensions for Active Inference:
    Drift rate v is proportional to the difference in Expected Free Energy (G).
    v = k * (G(action_1) - G(action_2))
    """
    pass
