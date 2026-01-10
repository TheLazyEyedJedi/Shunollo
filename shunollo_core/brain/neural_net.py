"""
neural_net.py
-------------
The Neural Substrate of Shunollo.
Implements a lightweight Reservoir Computing (Echo State Network) model.

Bio-Isomorphism:
- The "Reservoir" mimics the recurrent, chaotic connectivity of the cortex.
- The "Readout" mimics the trainable synaptic weights that extract meaning from the chaos.
- Supports "Online Learning" (Hebbian/Delta) suitable for real-time traffic analysis.
"""
import numpy as np
import os
from typing import Tuple, Optional

class LinearAssociativeMemory:
    """
    A simple specialized neural associative memory.
    Maps an Input Vector (18-dim Sensation) -> Output Scalar (Anomaly Probability).
    """
    def __init__(self, input_size: int = 18, reservoir_size: int = 100, spectral_radius: float = 0.9):
        self.input_size = input_size
        self.reservoir_size = reservoir_size
        self.learning_rate = 0.05 # Faster learning with better separation
        
        # 1. Fixed Recurrent Weights (The "Structure" of the Brain)
        np.random.seed(42) # Deterministic
        self.W_res = np.random.randn(reservoir_size, reservoir_size)
        
        rhoW = max(abs(np.linalg.eigvals(self.W_res)))
        self.W_res = self.W_res * (spectral_radius / rhoW)
        
        # 2. Input Weights (Sensory Projection)
        self.W_in = np.random.uniform(-1, 1, (reservoir_size, input_size))
        
        # 3. Fixed Reservoir Bias (To ensure separability of low magnitude inputs)
        # Mimics "Baseline Firing Rate"
        self.W_bias = np.random.uniform(-1, 1, (reservoir_size, 1))
        
        # 4. Trainable Output Weights (Synapses)
        self.W_out = np.zeros((1, reservoir_size))
        self.bias = 0.0 # Trainable output threshold
        
        # State vector (Short-term memory)
        self.state = np.zeros((reservoir_size, 1))

    def reset(self):
        """Clear short-term memory (Sleep/Reset)."""
        self.state = np.zeros((self.reservoir_size, 1))

    def forward(self, u: np.ndarray) -> dict:
        """
        Forward pass (Intuition).
        u: Input vector (shape [18] or [18, 1])
        Returns: Dict containing 'classification_score' (0.0-1.0) and 'anomaly_score' (Reconstruction error or similar)
        """
        if u.ndim == 1:
            u = u.reshape(-1, 1)
        
        # Input validation: Replace NaN/Inf with zeros for numerical stability
        if np.any(~np.isfinite(u)):
            u = np.nan_to_num(u, nan=0.0, posinf=0.0, neginf=0.0)
            
        # 1. Update Reservoir State (Recurrent Dynamics)
        # x(t) = tanh(W_in * u(t) + W_res * x(t-1) + W_bias)
        pre_activation = np.dot(self.W_in, u) + np.dot(self.W_res, self.state) + self.W_bias
        self.state = np.tanh(pre_activation)
        
        # 2. Readout (Linear Association)
        # y(t) = W_out * x(t) + bias
        output = np.dot(self.W_out, self.state) + self.bias
        
        # Numerically Stable Sigmoid
        val = output.item()
        if val >= 0:
            z = np.exp(-val)
            cls_score = 1.0 / (1.0 + z)
        else:
            z = np.exp(val)
            cls_score = z / (1.0 + z)
            
        # 3. Anomaly Score (Simplified for LinearAssociativeMemory)
        # Use reservoir state magnitude variance as a proxy for "surprise"?
        # Or just return 0.0 if not implemented.
        # But autoencoder has real anomaly score. 
        # For now, we return 0.0 placeholder or implement a basic energy metric.
        # Let's use the magnitude of the state vector change?
        # For consistency with the Neuro-Symbolic API, we return a dict.
        
        return {
            "classification_score": cls_score,
            "anomaly_score": 0.0 # Placeholder for Autoencoder integration
        }

    def train(self, u: np.ndarray, target: float):
        """
        Online Learning (Delta Rule / LMS).
        Adjusts W_out based on prediction error.
        """
        # Forward pass
        result = self.forward(u)
        prediction = result["classification_score"]
        
        # Error
        error = target - prediction
        
        # Hebbian Update: W_out += lr * error * state.T
        update = self.learning_rate * error * self.state.T
        self.W_out += update
        
        # Update Output Bias
        self.bias += self.learning_rate * error

    def save(self, path: str):
        """
        Secure Save using Numpy Zip (No Pickle).
        """
        np.savez_compressed(
            path,
            W_in=self.W_in,
            W_res=self.W_res,
            W_bias=self.W_bias,
            W_out=self.W_out,
            bias=np.array([self.bias]), # Wrap scaler
            state=self.state
        )
            
    def load(self, path: str):
        """
        Secure Load using Numpy Zip (No Pickle).
        """
        # Auto-append extension if missing
        if not path.endswith(".npz"):
            path += ".npz"
            
        if not os.path.exists(path): return
        
        try:
            with np.load(path) as data:
                self.W_in = data["W_in"]
                self.W_res = data["W_res"]
                self.W_bias = data.get("W_bias", np.zeros((self.reservoir_size, 1)))
                self.W_out = data["W_out"]
                # Unwrap scalar
                bias_val = data.get("bias", 0.0)
                self.bias = float(bias_val) if np.ndim(bias_val) == 0 else float(bias_val[0])
                self.state = data["state"]
        except Exception as e:
            print(f"Error loading Brain state from {path}: {e}")

# Global Instance (Singleton)
_cortex = LinearAssociativeMemory()

def get_brain(reset: bool = False) -> LinearAssociativeMemory:
    """
    Factory for the Brain.
    Args:
        reset: If True, creates a fresh brain (useful for testing).
    """
    global _cortex
    if reset:
        _cortex = LinearAssociativeMemory()
    return _cortex
