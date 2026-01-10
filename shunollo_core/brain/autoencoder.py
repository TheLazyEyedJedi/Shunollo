"""
autoencoder.py
--------------
The "Imagination" of Shunollo.
A simple Autoencoder for Anomaly Detection.

Bio-Isomorphism:
- The Brain constantly predicts (reconstructs) sensory input.
- "Surprise" (Prediction Error) = Reconstruction Error = Anomaly.
- If the brain cannot "imagine" the packet (based on what it knows is normal), it is alien.

Architecture:
Input (18) -> Encoder (12) -> Latent (6) -> Decoder (12) -> Output (18)
"""
import numpy as np
import os

class Autoencoder:
    def __init__(self, input_size: int = 18, hidden_size: int = 12, latent_size: int = 6):
        self.input_size = input_size
        self.learning_rate = 0.05 # Increased learning rate for faster convergence
        
        # Xavier/He-like Initialization (Better variance handling)
        np.random.seed(42)
        scale1 = np.sqrt(2.0 / (input_size + hidden_size))
        self.W_enc1 = np.random.randn(hidden_size, input_size) * scale1
        self.b_enc1 = np.zeros((hidden_size, 1))
        
        scale2 = np.sqrt(2.0 / (hidden_size + latent_size))
        self.W_enc2 = np.random.randn(latent_size, hidden_size) * scale2
        self.b_enc2 = np.zeros((latent_size, 1))
        
        # Decoder Weights
        self.W_dec1 = np.random.randn(hidden_size, latent_size) * scale2
        self.b_dec1 = np.zeros((hidden_size, 1))
        
        self.W_dec2 = np.random.randn(input_size, hidden_size) * scale1
        self.b_dec2 = np.zeros((input_size, 1))

    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -15, 15)))

    def _sigmoid_derivative(self, x):
        s = self._sigmoid(x)
        return s * (1 - s)

    def forward(self, x):
        """
        Pass x through Encoder -> Latent -> Decoder.
        Returns: (reconstruction, latent_vector)
        """
        if x.ndim == 1: x = x.reshape(-1, 1)
        
        # Input validation: Replace NaN/Inf with zeros for numerical stability
        if np.any(~np.isfinite(x)):
            x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Encoder
        self.z1 = np.dot(self.W_enc1, x) + self.b_enc1
        self.a1 = np.tanh(self.z1)
        
        self.z2 = np.dot(self.W_enc2, self.a1) + self.b_enc2
        self.latent = np.tanh(self.z2) # Latent representation
        
        # Decoder
        self.z3 = np.dot(self.W_dec1, self.latent) + self.b_dec1
        self.a3 = np.tanh(self.z3)
        
        self.z4 = np.dot(self.W_dec2, self.a3) + self.b_dec2
        # Output range 0-1 (Physics is normalized)
        self.reconstruction = self._sigmoid(self.z4) 
        
        return self.reconstruction, self.latent

    def calculate_anomaly_score(self, x) -> float:
        """
        Returns Mean Squared Error between Input and Reconstruction.
        High Error = Anomaly.
        """
        recon, _ = self.forward(x)
        if x.ndim == 1: x = x.reshape(-1, 1)
        loss = np.mean((x - recon) ** 2)
        return float(loss)

    def train_on_normal(self, x):
        """
        Train the Autoencoder to reconstruct this 'Normal' sample.
        Simple Backpropagation (SGD).
        """
        recon, _ = self.forward(x)
        if x.ndim == 1: x = x.reshape(-1, 1)
        
        # 1. Output Layer Error (MSE Gradient)
        # dL/dy = (y_hat - y) * sigmoid_derivative
        error_out = (recon - x) * self._sigmoid_derivative(self.z4)
        
        # 2. Backprop to Decoder 1
        # dL/dW_dec2 = error_out * a3.T
        grad_W_dec2 = np.dot(error_out, self.a3.T)
        grad_b_dec2 = error_out
        
        error_dec1 = np.dot(self.W_dec2.T, error_out) * (1 - self.a3**2) # tanh derivative
        grad_W_dec1 = np.dot(error_dec1, self.latent.T)
        grad_b_dec1 = error_dec1
        
        # 3. Backprop to Encoder 2
        error_enc2 = np.dot(self.W_dec1.T, error_dec1) * (1 - self.latent**2)
        grad_W_enc2 = np.dot(error_enc2, self.a1.T)
        grad_b_enc2 = error_enc2
        
        # 4. Backprop to Input
        error_enc1 = np.dot(self.W_enc2.T, error_enc2) * (1 - self.a1**2)
        grad_W_enc1 = np.dot(error_enc1, x.T)
        grad_b_enc1 = error_enc1
        
        # Updates
        lr = self.learning_rate
        self.W_dec2 -= lr * grad_W_dec2
        self.b_dec2 -= lr * grad_b_dec2
        self.W_dec1 -= lr * grad_W_dec1
        self.b_dec1 -= lr * grad_b_dec1
        
        self.W_enc2 -= lr * grad_W_enc2
        self.b_enc2 -= lr * grad_b_enc2
        self.W_enc1 -= lr * grad_W_enc1
        self.b_enc1 -= lr * grad_b_enc1

    def save(self, path):
        """
        Secure Save using Numpy Zip (No Pickle).
        """
        np.savez_compressed(
            path,
            W_enc1=self.W_enc1, b_enc1=self.b_enc1,
            W_enc2=self.W_enc2, b_enc2=self.b_enc2,
            W_dec1=self.W_dec1, b_dec1=self.b_dec1,
            W_dec2=self.W_dec2, b_dec2=self.b_dec2
        )

    def load(self, path):
        """
        Secure Load using Numpy Zip (No Pickle).
        """
        if not path.endswith(".npz"):
            path += ".npz"
            
        if not os.path.exists(path): return
        
        try:
            with np.load(path) as data:
                self.W_enc1 = data["W_enc1"]
                self.b_enc1 = data["b_enc1"]
                self.W_enc2 = data["W_enc2"]
                self.b_enc2 = data["b_enc2"]
                self.W_dec1 = data["W_dec1"]
                self.b_dec1 = data["b_dec1"]
                self.W_dec2 = data["W_dec2"]
                self.b_dec2 = data["b_dec2"]
        except Exception as e:
            print(f"Error loading Imagination state from {path}: {e}")

# Global "Imagination"
_imagination = Autoencoder()

def get_imagination():
    return _imagination
