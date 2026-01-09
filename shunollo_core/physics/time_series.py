"""
Shunollo Time Series Physics
============================
Physics of signal stability, chaos, and detection over time.
Handles Poisson statistics and Chaos Theory.
"""
import math
import statistics

class PoissonDetector:
    """Poisson statistics for quantum-limited signal detection."""
    def __init__(self, dark_noise: float = 0.01, threshold_events: int = 5):
        self.dark_noise = dark_noise
        self.threshold_events = threshold_events
    
    def detection_probability(self, mean_events: float) -> float:
        if mean_events <= 0: return 0.0
        cumulative = 0.0
        for k in range(self.threshold_events):
            try:
                p_k = (mean_events ** k) * math.exp(-mean_events) / math.factorial(k)
                cumulative += p_k
            except OverflowError: break
        return 1.0 - cumulative
    
    def signal_to_noise(self, signal_events: float) -> float:
        if signal_events <= 0: return 0.0
        total_events = signal_events + self.dark_noise
        noise = math.sqrt(total_events)
        return signal_events / noise if noise > 0 else 0.0
    
    def is_above_threshold(self, events: float, confidence: float = 0.95) -> bool:
        return self.detection_probability(events) >= confidence

def calculate_volatility_index(actual_val: float, expected_mean: float, sigma: float, dt: float = 1.0) -> float:
    """Brownian Motion / Bachelier Metric."""
    if sigma <= 0: return 1.0
    temporal_scaling = math.sqrt(max(0.1, dt))
    deviation = abs(actual_val - expected_mean) / (sigma * temporal_scaling)
    return min(1.0, deviation / 5.0) 

def calculate_lyapunov_exponent(values: list) -> float:
    """Chaos / Determinism filter."""
    if len(values) < 5: return 1.0
    diffs = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
    try:
        chaos = statistics.stdev(diffs) / (statistics.mean(diffs) + 1.0) if diffs else 1.0
        return min(1.0, chaos)
    except:
        return 1.0
