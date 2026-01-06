"""
preprocessor.py - The Clean Room
--------------------------------
StandardScaler implementation for normalizing network traffic data.
Uses Welford's Algorithm for online (streaming) variance updates.
"""
import math
import logging

# Configure logger
logger = logging.getLogger(__name__)

class StandardScaler:
    """
    Normalizes data to Z-Scores (mean=0, std=1).
    Supports online learning via partial_fit().
    """
    
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0 # Sum of squares of differences from the current mean
        self.std_dev = 0.0
        
    def fit(self, data: list[float]):
        """
        Compute mean and std_dev from a batch of data.
        Resets existing state.
        """
        logger.info(f"Fitting StandardScaler with {len(data)} samples...")
        self.reset()
        self.partial_fit(data)
        
    def partial_fit(self, data: list[float]):
        """
        Update mean and std_dev with new data (Online Learning).
        Uses Welford's Algorithm for numerical stability.
        """
        for x in data:
            self.count += 1
            delta = x - self.mean
            self.mean += delta / self.count
            delta2 = x - self.mean
            self.M2 += delta * delta2
            
        if self.count < 2:
            self.std_dev = 0.0
        else:
            self.std_dev = math.sqrt(self.M2 / (self.count - 1)) # Sample Std Dev
            
        logger.debug(f"partial_fit: N={self.count}, Mean={self.mean:.4f}, Std={self.std_dev:.4f}")

    def transform(self, value: float) -> float:
        """
        Convert a raw value to its Z-Score.
        Returns 0.0 if variance is zero.
        """
        if self.std_dev == 0:
            return 0.0
        
        z_score = (value - self.mean) / self.std_dev
        return z_score
        
    def reset(self):
        """Clear all internal stats."""
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.std_dev = 0.0
