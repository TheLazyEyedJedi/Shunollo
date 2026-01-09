"""
Shunollo Optics & Psychophysics
===============================
Physics of perception, distortion, and noise.
Handles Weber-Fechner Law, Lens Distortion, and Allan Variance.
"""
import numpy as np
import math

class Psychophysics:
    """Stevens' Power Law and Weber-Fechner for perceptual scaling."""
    EXPONENTS = {
        "brightness": 0.33, "loudness": 0.67, "vibration": 0.95,
        "pressure": 1.1, "temperature": 1.0, "pain": 3.5,
        "latency": 1.5, "throughput": 0.5, "default": 1.0,
    }
    
    @staticmethod
    def apply_stevens_law(value: float, modality: str = "default") -> float:
        n = Psychophysics.EXPONENTS.get(modality, 1.0)
        safe_value = max(0.0, min(1.0, value))
        return safe_value ** n if n != 1.0 else safe_value
    
    @staticmethod
    def calculate_jnd(intensity: float, weber_fraction: float = 0.1) -> float:
        return intensity * weber_fraction

class DistortionModel:
    """Brown-Conrady distortion model for data 'lens' effects."""
    def __init__(self, k1: float = 0.0, k2: float = 0.0, k3: float = 0.0, p1: float = 0.0, p2: float = 0.0):
        self.k1, self.k2, self.k3, self.p1, self.p2 = k1, k2, k3, p1, p2
    
    def distort(self, x: float, y: float) -> tuple:
        r2 = x*x + y*y
        r4 = r2*r2
        r6 = r4*r2
        radial = 1 + self.k1 * r2 + self.k2 * r4 + self.k3 * r6
        x_d = x * radial + 2 * self.p1 * x * y + self.p2 * (r2 + 2 * x * x)
        y_d = y * radial + self.p1 * (r2 + 2 * y * y) + 2 * self.p2 * x * y
        return (x_d, y_d)
    
    def undistort(self, x_d: float, y_d: float, iterations: int = 5) -> tuple:
        x, y = x_d, y_d
        for _ in range(iterations):
            x_est, y_est = self.distort(x, y)
            dx, dy = x_d - x_est, y_d - y_est
            x, y = x + dx, y + dy
            if dx*dx + dy*dy < 1e-12: break
        return (x, y)
    
    def distort_vector(self, vector: list, center_idx: int = None) -> list:
        n = len(vector)
        if n == 0: return vector
        if center_idx is None: center_idx = n // 2
        result = []
        for i, val in enumerate(vector):
            dist = (i - center_idx) / max(1, n / 2)
            r2 = dist * dist
            scale = 1 + self.k1 * r2 + self.k2 * r2 * r2
            result.append(val * scale)
        return result
    
    @staticmethod
    def attention_distortion(priority: float = 0.5) -> 'DistortionModel':
        k1 = priority * 0.3
        return DistortionModel(k1=k1, k2=0.0, k3=0.0)

class NoisePhysics:
    """Allan Variance noise characterization."""
    NOISE_TYPES = {
        'quantization': -1.0, 'random_walk': -0.5, 'bias_instability': 0.0,
        'rate_random_walk': 0.5, 'drift_ramp': 1.0,
    }
    
    @staticmethod
    def allan_variance(samples: list, sample_rate: float = 1.0) -> dict:
        n = len(samples)
        if n < 4: return {}
        data = np.array(samples, dtype=float)
        results = {}
        max_m = n // 4
        m = 1
        while m <= max_m:
            tau = m / sample_rate
            num_bins = n // m
            if num_bins < 2: break
            averages = data[:num_bins * m].reshape(-1, m).mean(axis=1)
            diffs = np.diff(averages)
            avar = 0.5 * np.mean(diffs ** 2)
            results[tau] = np.sqrt(avar) if avar > 0 else 0.0
            m *= 2
        return results
    
    @staticmethod
    def classify_noise(allan_results: dict) -> tuple:
        if len(allan_results) < 3: return ('unknown', 0.0, 0.0)
        taus = np.array(list(allan_results.keys()))
        sigmas = np.array(list(allan_results.values()))
        mask = sigmas > 0
        if np.sum(mask) < 3: return ('unknown', 0.0, 0.0)
        log_tau = np.log10(taus[mask])
        log_sigma = np.log10(sigmas[mask])
        coeffs = np.polyfit(log_tau, log_sigma, 1)
        slope = coeffs[0]
        predicted = np.polyval(coeffs, log_tau)
        ss_res = np.sum((log_sigma - predicted) ** 2)
        ss_tot = np.sum((log_sigma - np.mean(log_sigma)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        best_type = 'unknown'
        min_distance = float('inf')
        for n_type, c_slope in NoisePhysics.NOISE_TYPES.items():
            dist = abs(slope - c_slope)
            if dist < min_distance:
                min_distance = dist
                best_type = n_type
        return (best_type, float(slope), float(r_squared))

    @staticmethod
    def generate_noise(noise_type: str, n_samples: int, amplitude: float = 1.0) -> list:
        if noise_type == 'random_walk':
            return list(np.cumsum(np.random.randn(n_samples) * amplitude))
        elif noise_type == 'bias_instability':
            beta = 0.1
            noise = np.zeros(n_samples)
            for i in range(1, n_samples):
                noise[i] = (1 - beta) * noise[i-1] + beta * np.random.randn() * amplitude
            return list(noise)
        elif noise_type == 'drift_ramp':
            t = np.linspace(0, 1, n_samples)
            return list(t * amplitude + np.random.randn(n_samples) * 0.1 * amplitude)
        elif noise_type == 'rate_random_walk':
            return list(np.cumsum(np.cumsum(np.random.randn(n_samples) * amplitude)))
        else:
            return list(np.random.randn(n_samples) * amplitude)
            
    @staticmethod
    def sensor_health(allan_results: dict) -> tuple:
        noise_type, slope, confidence = NoisePhysics.classify_noise(allan_results)
        if noise_type == 'random_walk': return (0.9, "Normal: White noise floor")
        elif noise_type == 'bias_instability': return (0.7, "Caution: Bias drifting")
        elif noise_type == 'rate_random_walk': return (0.4, "Warning: Hardware aging")
        elif noise_type == 'drift_ramp': return (0.2, "Critical: Systematic drift")
        else: return (0.5, f"Unknown: slope={slope:.2f}")
