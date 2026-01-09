"""
Hermite-Gaussian Mode Decomposition for Spectral Analysis
----------------------------------------------------------
Projects signals onto Hermite-Gaussian basis for enhanced resolution,
inspired by SPADE (SPAtial Demultiplexing) from quantum optics.

Mathematical Foundation:
    Hermite-Gaussian: ψ_n(t) = (1/√(2^n n! √π)) H_n(t) exp(-t²/2)
    Mode coefficients: c_n = ∫ f(t) ψ_n(t) dt
    Sub-Rayleigh offset: δ ≈ c_1 / (c_0 · √E) where E = signal energy

Limitations:
    - Integration truncated to [-4, 4], reduces orthonormality for n > 5
    - Numerical issues for n > 20 despite log-domain normalization
    - Signal separation assumes orthogonal mode occupancy

References:
    Tsang et al. (2016). Quantum theory of superresolution for two
    incoherent sources. Phys. Rev. X.
"""
import numpy as np
from typing import Tuple, List, Dict, Optional
import warnings
import scipy.special

__all__ = [
    'SPADEAnalyzer',
    'create_spade_analyzer',
    'MAX_SAFE_MODE',
    'INTEGRATION_BOUNDS',
]

MAX_SAFE_MODE = 20
INTEGRATION_BOUNDS = (-4.0, 4.0)


class SPADEAnalyzer:
    """
    Hermite-Gaussian mode projection for spectral analysis.
    
    Decomposes signals into "shape components" rather than frequency
    components (Fourier). Useful for detecting subtle deviations from
    expected waveform shapes.
    
    Attributes:
        max_modes: Number of HG modes to compute (0 to max_modes-1)
    """
    
    __slots__ = ('max_modes',)
    
    def __init__(self, max_modes: int = 6) -> None:
        """
        Initialize the analyzer.
        
        Args:
            max_modes: Number of HG modes to compute
            
        Raises:
            ValueError: If max_modes is not positive
        """
        if max_modes <= 0:
            raise ValueError(f"max_modes must be positive, got {max_modes}")
        if max_modes > MAX_SAFE_MODE:
            warnings.warn(
                f"max_modes={max_modes} may cause numerical issues. "
                f"Recommended max: {MAX_SAFE_MODE}"
            )
        
        self.max_modes = max_modes
    
    def __repr__(self) -> str:
        return f"SPADEAnalyzer(max_modes={self.max_modes})"
    
    def hermite_gaussian_mode(self, n: int, t: np.ndarray) -> np.ndarray:
        """
        Compute normalized Hermite-Gaussian mode ψ_n(t).
        
        Uses log-domain normalization and scipy for numerical stability.
        
        Args:
            n: Mode number (0, 1, 2, ...)
            t: Time/position array (normalized ~ [-4, 4])
        
        Returns:
            Normalized HG mode values at each t
            
        Raises:
            ValueError: If n >= max_modes
        """
        if n >= self.max_modes:
            raise ValueError(f"Mode {n} >= max_modes {self.max_modes}")
        
        if n > MAX_SAFE_MODE:
            warnings.warn(f"Mode {n} > {MAX_SAFE_MODE}, numerical issues possible")
        
        log_norm = -0.5 * (
            n * np.log(2) + 
            scipy.special.gammaln(n + 1) +
            0.25 * np.log(np.pi)
        )
        norm = np.exp(log_norm)
        
        H_n = scipy.special.hermite(n)(t)
        gaussian = np.exp(-t**2 / 2)
        
        return norm * H_n * gaussian
    
    def verify_orthonormality(self, n_samples: int = 1000) -> Dict[str, float]:
        """
        Verify mode orthonormality numerically.
        
        Returns dict with maximum off-diagonal inner product and
        maximum deviation from unity on diagonal.
        """
        t = np.linspace(INTEGRATION_BOUNDS[0], INTEGRATION_BOUNDS[1], n_samples)
        max_off_diagonal = 0.0
        max_diagonal_error = 0.0
        
        for i in range(self.max_modes):
            mode_i = self.hermite_gaussian_mode(i, t)
            for j in range(i, self.max_modes):
                mode_j = self.hermite_gaussian_mode(j, t)
                inner = np.trapezoid(mode_i * mode_j, t)
                
                if i == j:
                    max_diagonal_error = max(max_diagonal_error, abs(inner - 1.0))
                else:
                    max_off_diagonal = max(max_off_diagonal, abs(inner))
        
        return {
            "max_off_diagonal": max_off_diagonal,
            "max_diagonal_error": max_diagonal_error,
            "orthonormal": max_off_diagonal < 0.01 and max_diagonal_error < 0.01
        }
    
    def project_to_modes(
        self, 
        signal: np.ndarray,
        preserve_amplitude: bool = False
    ) -> np.ndarray:
        """
        Decompose signal into HG mode coefficients.
        
        Args:
            signal: Time-series signal
            preserve_amplitude: If True, don't normalize signal
        
        Returns:
            Array of coefficients [c_0, c_1, ..., c_{N-1}]
        """
        n_samples = len(signal)
        if n_samples == 0:
            return np.zeros(self.max_modes)
        
        t = np.linspace(INTEGRATION_BOUNDS[0], INTEGRATION_BOUNDS[1], n_samples)
        
        if preserve_amplitude:
            signal_proc = signal.astype(float)
        else:
            norm = np.linalg.norm(signal)
            signal_proc = signal / (norm + 1e-10)
        
        coefficients = np.zeros(self.max_modes)
        for n in range(self.max_modes):
            mode = self.hermite_gaussian_mode(n, t)
            coefficients[n] = np.trapezoid(signal_proc * mode, t)
        
        return coefficients
    
    def detect_shadow_signal(
        self,
        signal: np.ndarray,
        noise_floor: float = 0.05
    ) -> Tuple[bool, float, float]:
        """
        Detect hidden "shadow" signal using mode ratio analysis.
        
        Computes δ ≈ c_1 / (c_0 · √E) where E is signal energy.
        If |c_1/c_0| > noise_floor, a hidden offset signal may exist.
        
        Args:
            signal: Input time-series
            noise_floor: Detection threshold for c_1/c_0 ratio
        
        Returns:
            Tuple of (detected, estimated_offset, confidence)
        """
        coeffs = self.project_to_modes(signal, preserve_amplitude=True)
        
        c_0 = abs(coeffs[0])
        c_1 = abs(coeffs[1])
        
        if c_0 < 1e-10:
            return False, 0.0, 0.0
        
        ratio = c_1 / c_0
        
        signal_energy = np.sum(signal.astype(float) ** 2)
        if signal_energy < 1e-10:
            return False, 0.0, 0.0
        
        delta = c_1 / (c_0 * np.sqrt(signal_energy))
        detected = ratio > noise_floor
        confidence = min(1.0, ratio / noise_floor) if noise_floor > 0 else 0.0
        
        return detected, delta, confidence
    
    def reconstruct_from_modes(
        self,
        coefficients: np.ndarray,
        n_samples: int
    ) -> np.ndarray:
        """
        Reconstruct signal from HG mode coefficients.
        
        Args:
            coefficients: Mode coefficients
            n_samples: Number of output samples
        
        Returns:
            Reconstructed signal
        """
        t = np.linspace(INTEGRATION_BOUNDS[0], INTEGRATION_BOUNDS[1], n_samples)
        reconstructed = np.zeros(n_samples)
        
        for n in range(min(len(coefficients), self.max_modes)):
            mode = self.hermite_gaussian_mode(n, t)
            reconstructed += coefficients[n] * mode
        
        return reconstructed
    
    def analyze_mode_spectrum(
        self,
        signal: np.ndarray,
        preserve_amplitude: bool = True
    ) -> Dict:
        """
        Return detailed mode analysis.
        
        Returns:
            Dict with coefficients, energies, energy_fractions,
            dominant_mode, c1_c0_ratio, orthogonality_warning, total_energy
        """
        coeffs = self.project_to_modes(signal, preserve_amplitude=preserve_amplitude)
        
        energies = coeffs ** 2
        total_energy = np.sum(energies)
        
        if total_energy > 0:
            fractions = energies / total_energy
        else:
            fractions = np.zeros_like(energies)
        
        high_mode_energy = np.sum(energies[4:]) / (total_energy + 1e-10)
        
        return {
            "coefficients": coeffs.tolist(),
            "energies": energies.tolist(),
            "energy_fractions": fractions.tolist(),
            "dominant_mode": int(np.argmax(np.abs(coeffs))),
            "c1_c0_ratio": abs(coeffs[1] / coeffs[0]) if abs(coeffs[0]) > 1e-10 else 0.0,
            "orthogonality_warning": high_mode_energy > 0.1,
            "total_energy": total_energy
        }
    
    def estimate_separation_feasibility(
        self,
        combined: np.ndarray,
        n_expected_signals: int = 2
    ) -> Dict:
        """
        Estimate whether overlapping signals can be separated.
        
        Perfect separation requires signals to occupy different mode
        subspaces, which is rarely true for similar frequencies.
        
        Returns:
            Dict with feasibility, mode_entropy, warning, and spectrum
        """
        spectrum = self.analyze_mode_spectrum(combined)
        fractions = np.array(spectrum["energy_fractions"])
        
        fractions_nonzero = fractions[fractions > 1e-10]
        if len(fractions_nonzero) > 0:
            entropy = -np.sum(fractions_nonzero * np.log(fractions_nonzero))
            max_entropy = np.log(len(fractions_nonzero))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        else:
            normalized_entropy = 0.0
        
        if normalized_entropy > 0.7:
            feasibility = "HIGH"
        elif normalized_entropy > 0.4:
            feasibility = "MEDIUM"
        else:
            feasibility = "LOW"
        
        return {
            "feasibility": feasibility,
            "mode_entropy": normalized_entropy,
            "warning": "Separation assumes orthogonal mode occupancy",
            "spectrum": spectrum
        }


def create_spade_analyzer(max_modes: int = 6) -> SPADEAnalyzer:
    """Create a SPADEAnalyzer instance."""
    return SPADEAnalyzer(max_modes=max_modes)
