"""
Stochastic Resonance for Sub-Threshold Signal Detection
--------------------------------------------------------
Boosts weak signals by injecting controlled noise using Langevin dynamics
on a bistable potential.

Mathematical Foundation:
    Langevin Equation: dx/dt = -dU/dx + S(t) + ξ(t)
    Bistable Potential: U(x) = -x²/2 + x⁴/4 (barrier ΔV = 0.25)
    Optimal Noise: D_opt ≈ ΔV / 2
    White Noise: ⟨ξ(t)ξ(t')⟩ = 2D δ(t-t')

Euler-Maruyama Discretization:
    x_{n+1} = x_n + Δt·(-U'(x_n) + S_n) + √(2D·Δt)·η_n
    where η_n ~ N(0, 1)

This is a rate-code approximation using continuous dynamics. For spike-based
stochastic resonance, use integrate-and-fire models.

References:
    Gammaitoni et al. (1998). Stochastic resonance. Rev. Mod. Phys.
    McDonnell & Abbott (2009). What is stochastic resonance?
"""
import numpy as np
from typing import Tuple, Optional
import warnings

__all__ = [
    'StochasticResonator',
    'create_resonator',
    'STANDARD_BARRIER_HEIGHT',
    'MIN_DT',
    'MAX_DT',
]

STANDARD_BARRIER_HEIGHT = 0.25
MIN_DT = 1e-6
MAX_DT = 1.0


class StochasticResonator:
    """
    Stochastic resonance for sub-threshold signal detection.
    
    In bistable systems, controlled noise injection can paradoxically improve
    signal detection by helping weak signals cross the threshold between
    stable states.
    
    Attributes:
        delta_v: Potential barrier height
        threshold: Detection threshold for output signal
        d_opt: Optimal noise intensity (ΔV / 2)
    """
    
    __slots__ = ('delta_v', 'threshold', 'd_opt', '_rng')
    
    def __init__(
        self, 
        barrier_height: Optional[float] = None, 
        threshold: float = 0.5,
        random_seed: Optional[int] = None
    ) -> None:
        """
        Initialize the resonator.
        
        Args:
            barrier_height: Potential barrier ΔV (defaults to 0.25 for standard potential)
            threshold: Detection threshold for output signal
            random_seed: For reproducibility
            
        Raises:
            ValueError: If barrier_height is not positive
        """
        if barrier_height is None:
            self.delta_v = STANDARD_BARRIER_HEIGHT
        else:
            if barrier_height <= 0:
                raise ValueError(f"barrier_height must be positive, got {barrier_height}")
            self.delta_v = barrier_height
        
        self.threshold = threshold
        self.d_opt = self.delta_v / 2.0
        self._rng = np.random.default_rng(random_seed)
    
    def __repr__(self) -> str:
        return (
            f"StochasticResonator(delta_v={self.delta_v}, "
            f"d_opt={self.d_opt}, threshold={self.threshold})"
        )
    
    def bistable_potential(self, x: np.ndarray) -> np.ndarray:
        """
        Evaluate double-well potential U(x) = -x²/2 + x⁴/4.
        
        Properties:
            - Minima at x = ±1: U(±1) = -0.25
            - Maximum at x = 0: U(0) = 0
            - Barrier height: ΔV = 0.25
        """
        return -0.5 * x**2 + 0.25 * x**4
    
    def potential_gradient(self, x: np.ndarray) -> np.ndarray:
        """
        Evaluate potential gradient dU/dx = -x + x³.
        
        Includes clamping to prevent overflow for large x values.
        """
        # Clamp to prevent overflow (|x| > 1e100 causes x**3 overflow)
        x_safe = np.clip(x, -1e50, 1e50)
        return -x_safe + x_safe**3
    
    def apply_resonance(
        self,
        signal: np.ndarray,
        noise_intensity: Optional[float] = None,
        dt: float = 0.01
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply stochastic resonance via Langevin dynamics.
        
        Uses Euler-Maruyama integration with noise amplitude √(2·D·Δt).
        
        Note:
            The last element of signal is not used due to the integration
            scheme evaluating at i-1 for consistency.
        
        Args:
            signal: Input signal (potentially sub-threshold)
            noise_intensity: D parameter (defaults to d_opt)
            dt: Time step for simulation
        
        Returns:
            Tuple of (output_trajectory, noise_samples)
            
        Raises:
            ValueError: If dt is out of stable range
        """
        if dt < MIN_DT:
            raise ValueError(
                f"dt={dt} too small (< {MIN_DT}), causes numerical instability"
            )
        if dt > MAX_DT:
            warnings.warn(f"dt={dt} is large, may reduce accuracy")
        
        if noise_intensity is None:
            noise_intensity = self.d_opt
        
        if noise_intensity < 0:
            raise ValueError(f"noise_intensity must be non-negative, got {noise_intensity}")
        
        n = len(signal)
        if n == 0:
            return np.array([]), np.array([])
        
        x = np.zeros(n)
        eta = self._rng.standard_normal(n)
        noise_scale = np.sqrt(2 * noise_intensity * dt)
        
        for i in range(1, n):
            drift = -self.potential_gradient(x[i-1])
            x[i] = x[i-1] + dt * (drift + signal[i-1]) + noise_scale * eta[i]
        
        return x, eta * noise_scale
    
    def detect_subthreshold(
        self,
        signal: np.ndarray,
        noise_trials: int = 10
    ) -> Tuple[bool, float, np.ndarray]:
        """
        Detect sub-threshold signals using ensemble averaging.
        
        Multiple noise realizations reveal hidden signals:
        noise cancels (random) while signal adds coherently (deterministic).
        
        Args:
            signal: Input signal to analyze
            noise_trials: Number of noise realizations for averaging
        
        Returns:
            Tuple of (detected, confidence, averaged_output)
            
        Raises:
            ValueError: If noise_trials < 1
        """
        if noise_trials < 1:
            raise ValueError(f"noise_trials must be >= 1, got {noise_trials}")
        
        if len(signal) == 0:
            return False, 0.0, np.array([])
        
        outputs = [self.apply_resonance(signal)[0] for _ in range(noise_trials)]
        averaged = np.mean(outputs, axis=0)
        
        crossings = np.sum(np.abs(averaged) > self.threshold)
        crossing_ratio = crossings / len(averaged)
        
        detected = crossing_ratio > 0.1
        confidence = min(1.0, crossing_ratio * 2)
        
        return detected, confidence, averaged
    
    def compute_spectral_snr(
        self,
        signal: np.ndarray,
        signal_freq_hz: float,
        sampling_rate_hz: float,
        noise_intensity: Optional[float] = None
    ) -> float:
        """
        Compute Signal-to-Noise Ratio in the frequency domain.
        
        SNR = Power at signal frequency / Broadband noise power
        
        Args:
            signal: Input signal (should be periodic at signal_freq_hz)
            signal_freq_hz: Expected signal frequency
            sampling_rate_hz: Sampling rate of the signal
            noise_intensity: D parameter for noise injection
        
        Returns:
            SNR in dB
        """
        output, _ = self.apply_resonance(signal, noise_intensity)
        
        n = len(output)
        freqs = np.fft.fftfreq(n, 1.0 / sampling_rate_hz)
        spectrum = np.abs(np.fft.fft(output)) ** 2 / n
        
        signal_bin = np.argmin(np.abs(freqs - signal_freq_hz))
        signal_power = spectrum[signal_bin]
        
        noise_bins = np.ones(len(spectrum), dtype=bool)
        noise_bins[signal_bin] = False
        noise_bins[0] = False
        noise_power = np.mean(spectrum[noise_bins])
        
        if noise_power > 0:
            return 10 * np.log10(signal_power / noise_power)
        return float('inf')
    
    def find_optimal_noise(
        self,
        signal: np.ndarray,
        d_range: Tuple[float, float] = (0.01, 1.0),
        steps: int = 20,
        signal_freq_hz: float = 1.0,
        sampling_rate_hz: float = 100.0
    ) -> Tuple[float, float]:
        """
        Find optimal noise intensity by scanning D values.
        
        Stochastic resonance has a characteristic inverted-U shaped
        SNR curve with a peak at D_opt.
        
        Returns:
            Tuple of (optimal_d, max_snr_db)
        """
        d_values = np.linspace(d_range[0], d_range[1], steps)
        snr_values = [
            self.compute_spectral_snr(signal, signal_freq_hz, sampling_rate_hz, d)
            for d in d_values
        ]
        
        max_idx = np.argmax(snr_values)
        return d_values[max_idx], snr_values[max_idx]
    
    def set_barrier_height(self, delta_v: float) -> None:
        """Update barrier height and recalculate optimal noise."""
        if delta_v <= 0:
            raise ValueError(f"barrier_height must be positive, got {delta_v}")
        self.delta_v = delta_v
        self.d_opt = self.delta_v / 2.0
    
    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self._rng = np.random.default_rng(seed)


def create_resonator(
    barrier_height: Optional[float] = None,
    random_seed: Optional[int] = None
) -> StochasticResonator:
    """Create a StochasticResonator instance."""
    return StochasticResonator(
        barrier_height=barrier_height,
        random_seed=random_seed
    )
