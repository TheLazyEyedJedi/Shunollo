"""
example_stochastic_resonance.py
-------------------------------
Using Stochastic Resonance for Weak Signal Detection

This example shows how noise can paradoxically IMPROVE signal detection.
Think of it as "turning up the static to hear the whisper."

Domain: Sensor networks, weak signal processing, IoT
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from shunollo_core.perception.stochastic_resonance import StochasticResonator


def demonstrate_resonance():
    """Show how noise helps detect sub-threshold signals."""
    print("=" * 60)
    print("STOCHASTIC RESONANCE: Noise-Enhanced Signal Detection")
    print("=" * 60)
    
    # Create a VERY weak signal (below detection threshold)
    t = np.linspace(0, 10, 1000)
    weak_signal = np.sin(2 * np.pi * 0.5 * t) * 0.1  # Amplitude = 0.1
    
    print(f"\nSignal amplitude: 0.1 (very weak)")
    print(f"Detection threshold: 0.5")
    print(f"Without noise: signal is INVISIBLE\n")
    
    resonator = StochasticResonator(random_seed=42)
    
    # Test different noise levels
    noise_levels = [0.01, 0.05, 0.125, 0.3, 0.5]
    
    print("Noise Level | Detected | Confidence")
    print("-" * 40)
    
    for noise in noise_levels:
        detected, confidence, _ = resonator.detect_subthreshold(
            weak_signal, noise_trials=20
        )
        resonator._rng = np.random.default_rng(42)  # Reset for consistency
        
        # Manually run with specific noise level
        outputs = []
        for _ in range(20):
            out, _ = resonator.apply_resonance(weak_signal, noise_intensity=noise)
            outputs.append(out)
        averaged = np.mean(outputs, axis=0)
        crossings = np.sum(np.abs(averaged) > 0.5) / len(averaged)
        
        status = "[OK] YES" if crossings > 0.1 else "[X] NO "
        print(f"  D = {noise:.3f}  |  {status}   | {crossings*100:.1f}%")
    
    print(f"\nOptimal noise (D_opt): {resonator.d_opt:.3f}")
    print("The signal becomes detectable when noise ~ D_opt!")


def demonstrate_snr_curve():
    """Show the characteristic inverted-U SNR curve."""
    print("\n" + "=" * 60)
    print("SNR vs NOISE: The Inverted-U Curve")
    print("=" * 60)
    
    resonator = StochasticResonator(random_seed=42)
    
    # Create periodic signal
    t = np.linspace(0, 10, 500)
    signal = np.sin(2 * np.pi * 1.0 * t) * 0.15
    
    # Scan noise levels
    optimal_d, max_snr = resonator.find_optimal_noise(
        signal,
        d_range=(0.01, 0.5),
        steps=10,
        signal_freq_hz=1.0,
        sampling_rate_hz=50.0
    )
    
    print(f"\nOptimal noise intensity: D = {optimal_d:.3f}")
    print(f"Maximum SNR achieved: {max_snr:.1f} dB")
    print("\nThis is the 'sweet spot' where noise helps most!")


def practical_application():
    """Show a practical IoT sensor application."""
    print("\n" + "=" * 60)
    print("PRACTICAL: Detecting Weak Seismic Vibrations")
    print("=" * 60)
    
    # Simulate a seismic sensor with background noise
    np.random.seed(42)
    t = np.linspace(0, 5, 500)
    
    # Very weak earthquake precursor + sensor noise
    precursor = np.sin(2 * np.pi * 2 * t) * 0.05  # Amplitude 0.05
    sensor_noise = np.random.randn(500) * 0.02
    raw_signal = precursor + sensor_noise
    
    print("\nRaw sensor data: Precursor buried in noise")
    print(f"  Precursor amplitude: 0.05")
    print(f"  Sensor noise: +/-0.02")
    
    resonator = StochasticResonator(barrier_height=0.1, random_seed=42)
    
    # Try to detect without SR
    max_raw = np.max(np.abs(raw_signal))
    print(f"\nWithout SR: max amplitude = {max_raw:.3f}")
    print(f"  Threshold = 0.5 -> NOT DETECTED")
    
    # Apply stochastic resonance
    detected, confidence, enhanced = resonator.detect_subthreshold(
        raw_signal, noise_trials=50
    )
    
    max_enhanced = np.max(np.abs(enhanced))
    print(f"\nWith SR: max amplitude = {max_enhanced:.3f}")
    print(f"  Detected: {detected}, Confidence: {confidence:.1%}")
    
    if detected:
        print("\n[!] SEISMIC PRECURSOR DETECTED!")
        print("   This signal was INVISIBLE without stochastic resonance.")


if __name__ == "__main__":
    demonstrate_resonance()
    demonstrate_snr_curve()
    practical_application()
    print("\n[DONE] Stochastic resonance example complete!")
