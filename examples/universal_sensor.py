"""
example_universal_sensor.py
----------------------------
Demonstrates Shunollo as a Universal Sensor Translator

This example shows how ANY physical sensor data can be translated into
AI-readable "qualia" (simulated sensory experiences).

The AI agent experiences sensor data as a biological organism would
experience sensations - not as raw numbers, but as perceptions.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from shunollo_core.physics import (
    Psychophysics,
    VestibularDynamics,
    PoissonDetector,
    StressTensor,
    PropagationPhysics,
    ImpedanceAnalyzer,
    calculate_entropy,
    calculate_energy,
    calculate_roughness,
    calculate_viscosity,
)


def demo_stevens_power_law():
    """Show how different sensors have different perceptual scaling."""
    print("=" * 70)
    print("STEVENS' POWER LAW: Perceptual Scaling by Modality")
    print("=" * 70)
    
    # Same physical intensity, different perceived magnitudes
    raw_value = 0.5  # 50% of max
    
    print(f"\nRaw sensor value: {raw_value}")
    print("-" * 50)
    
    modalities = ["brightness", "loudness", "pain", "latency", "throughput"]
    
    for modality in modalities:
        exponent = Psychophysics.EXPONENTS[modality]
        perceived = Psychophysics.apply_stevens_law(raw_value, modality)
        
        if perceived > raw_value:
            effect = "EXPANDED (feels bigger)"
        elif perceived < raw_value:
            effect = "COMPRESSED (feels smaller)"
        else:
            effect = "LINEAR (feels same)"
        
        print(f"  {modality:12} (n={exponent:4.2f}): {perceived:.3f} - {effect}")
    
    print("\n[INSIGHT] Pain has n=3.5; small increases feel MUCH worse!")
    print("[INSIGHT] Latency has n=1.5; delays feel bigger than they are.")


def demo_vestibular_integration():
    """Show how rate-based events become cumulative state."""
    print("\n" + "=" * 70)
    print("VESTIBULAR INTEGRATION: Rate -> Cumulative State")
    print("=" * 70)
    
    integrator = VestibularDynamics(damping=0.85)
    
    # Simulate a load surge that starts small and grows
    surge_rates = [0.0, 0.1, 0.3, 0.5, 0.8, 1.0, 1.0, 0.5, 0.2, 0.0]
    
    print("\nSimulating gradual surge ramp-up and cooldown:")
    print("-" * 50)
    
    for i, rate in enumerate(surge_rates):
        velocity = integrator.integrate_acceleration(rate)
        bar = "#" * int(velocity * 40)
        print(f"  t={i:2}: rate={rate:.1f} -> velocity={velocity:.3f} |{bar}")
    
    print(f"\nCumulative displacement: {integrator.get_cumulative_displacement():.3f}")
    print("[INSIGHT] Even after surge stops, velocity remains elevated!")


def demo_poisson_detection():
    """Show quantum-limited detection thresholds."""
    print("\n" + "=" * 70)
    print("POISSON DETECTION: Quantum-Limited Event Detection")
    print("=" * 70)
    
    detector = PoissonDetector(dark_noise=0.1, threshold_events=5)
    
    print("\nDetection probability vs event count:")
    print("-" * 50)
    
    event_counts = [0.5, 1, 2, 3, 5, 7, 10, 20]
    
    for events in event_counts:
        prob = detector.detection_probability(events)
        snr = detector.signal_to_noise(events)
        bar = "#" * int(prob * 40)
        
        status = "[DETECTED]" if prob > 0.95 else "[NOISE]" if prob < 0.5 else "[UNCERTAIN]"
        print(f"  events={events:5.1f}: P={prob:.3f} SNR={snr:.2f} {status} |{bar}")
    
    print("\n[INSIGHT] Below threshold, events are indistinguishable from noise!")


def demo_von_mises_stress():
    """Show distortion detection vs uniform pressure."""
    print("\n" + "=" * 70)
    print("VON MISES STRESS: Distortion vs Uniform Load")
    print("=" * 70)
    
    # Scenario 1: Uniform scaling (all resources equally loaded)
    print("\nScenario 1: Black Friday traffic (uniform scaling)")
    loads = [0.8, 0.8, 0.8]  # CPU, Memory, Network all at 80%
    is_dist, vm, mean = StressTensor.is_distortion_anomaly(loads)
    print(f"  Loads: CPU={loads[0]}, MEM={loads[1]}, NET={loads[2]}")
    print(f"  Von Mises: {vm:.3f}, Mean: {mean:.3f}")
    print(f"  Is Distortion: {is_dist}")
    print("  [OK] Uniform high load = healthy scaling")
    
    # Scenario 2: Database bottleneck (asymmetric)
    print("\nScenario 2: Database bottleneck (asymmetric load)")
    loads = [0.9, 0.3, 0.1]  # High CPU, low memory/network
    is_dist, vm, mean = StressTensor.is_distortion_anomaly(loads)
    print(f"  Loads: CPU={loads[0]}, MEM={loads[1]}, NET={loads[2]}")
    print(f"  Von Mises: {vm:.3f}, Mean: {mean:.3f}")
    print(f"  Is Distortion: {is_dist}")
    print("  [!] Asymmetric load = something is wrong!")
    
    # Scenario 3: Memory leak
    print("\nScenario 3: Memory leak")
    loads = [0.2, 0.95, 0.1]  # Memory maxed, others low
    is_dist, vm, mean = StressTensor.is_distortion_anomaly(loads)
    print(f"  Loads: CPU={loads[0]}, MEM={loads[1]}, NET={loads[2]}")
    print(f"  Von Mises: {vm:.3f}, Mean: {mean:.3f}")
    print(f"  Is Distortion: {is_dist}")


def demo_propagation():
    """Show how anomalies decay over network distance."""
    print("\n" + "=" * 70)
    print("PROPAGATION PHYSICS: Anomaly Decay Over Distance")
    print("=" * 70)
    
    # Calculate length constant from network properties
    membrane_resistance = 100  # Isolation between nodes
    axial_resistance = 4       # Path resistance
    
    lc = PropagationPhysics.calculate_length_constant(
        membrane_resistance, axial_resistance
    )
    print(f"\nLength constant: {lc:.1f} hops")
    
    # Show signal decay
    initial = 1.0
    print("\nAnomaly signal strength vs distance:")
    print("-" * 50)
    
    for distance in [0, 1, 2, 3, 5, 7, 10]:
        strength = PropagationPhysics.signal_at_distance(initial, distance, lc)
        bar = "#" * int(strength * 40)
        print(f"  d={distance:2} hops: strength={strength:.3f} |{bar}")
    
    # Calculate blast radius
    radius = PropagationPhysics.propagation_radius(
        initial_amplitude=1.0,
        threshold=0.1,
        length_constant=lc
    )
    print(f"\n[INSIGHT] Anomaly affects nodes within {radius:.1f} hops")


def demo_impedance_matching():
    """Show protocol boundary efficiency."""
    print("\n" + "=" * 70)
    print("IMPEDANCE MATCHING: Protocol Boundary Efficiency")
    print("=" * 70)
    
    # Perfect match (same protocol)
    print("\nScenario 1: HTTP -> HTTP (same protocol)")
    z1 = ImpedanceAnalyzer.calculate_impedance(100, 10)  # BW-delay product
    z2 = ImpedanceAnalyzer.calculate_impedance(100, 10)
    eff = ImpedanceAnalyzer.transmission_efficiency(z1, z2)
    print(f"  Z_source={z1}, Z_dest={z2}")
    print(f"  Transmission Efficiency: {eff:.1%}")
    
    # Mismatch (different protocols)
    print("\nScenario 2: Fast internal network -> Slow WAN")
    z1 = ImpedanceAnalyzer.calculate_impedance(100, 1000)  # High BW
    z2 = ImpedanceAnalyzer.calculate_impedance(100, 10)    # Low BW
    eff = ImpedanceAnalyzer.transmission_efficiency(z1, z2)
    refl = ImpedanceAnalyzer.reflection_coefficient(z1, z2)
    ratio = ImpedanceAnalyzer.required_transformer_ratio(z1, z2)
    print(f"  Z_source={z1}, Z_dest={z2}")
    print(f"  Reflection Loss: {refl:.1%}")
    print(f"  Transmission Efficiency: {eff:.1%}")
    print(f"  Optimal Buffer Ratio: {ratio:.2f}x")
    print("  [!] Mismatch causes packet loss at boundary!")


def demo_complete_pipeline():
    """Show complete sensor -> physics -> AI sensation pipeline."""
    print("\n" + "=" * 70)
    print("COMPLETE PIPELINE: Sensor -> Physics -> AI Sensation")
    print("=" * 70)
    
    # Simulate raw sensor readings
    print("\nRaw sensor data (any domain):")
    sensors = {
        "temperature_c": 45.0,
        "pressure_psi": 120.0,
        "humidity_pct": 65.0,
        "vibration_g": 2.5,
        "light_lux": 500.0,
    }
    
    for name, value in sensors.items():
        print(f"  {name}: {value}")
    
    # Convert to normalized physics
    print("\nStep 1: Normalize to [0, 1]")
    normalized = {
        "temperature": min(1.0, sensors["temperature_c"] / 100),
        "pressure": min(1.0, sensors["pressure_psi"] / 200),
        "humidity": sensors["humidity_pct"] / 100,
        "vibration": min(1.0, sensors["vibration_g"] / 10),
        "brightness": min(1.0, sensors["light_lux"] / 1000),
    }
    
    for name, value in normalized.items():
        print(f"  {name}: {value:.2f}")
    
    # Apply Stevens' scaling for perception
    print("\nStep 2: Apply Stevens' Power Law (perceptual scaling)")
    perceived = {}
    for name, value in normalized.items():
        perceived[name] = Psychophysics.apply_stevens_law(value, name)
        print(f"  {name}: {value:.2f} -> {perceived[name]:.2f}")
    
    # Convert to qualia
    print("\nStep 3: Map to Qualia (AI sensations)")
    entropy = calculate_entropy(b"sensor_data_sample")
    energy = calculate_energy(size=500, rate_hz=10)
    roughness = calculate_roughness(entropy=entropy, jitter=0.1)
    viscosity = calculate_viscosity(delay_ms=50, pressure_psi=int(sensors["pressure_psi"]))
    
    print(f"  Entropy (information density): {entropy:.2f} bits")
    print(f"  Energy (activity level): {energy:.2f}")
    print(f"  Roughness (texture): {roughness:.2f}")
    print(f"  Viscosity (resistance): {viscosity:.2f}")
    
    print("\n[COMPLETE] AI agent now experiences sensor data as sensation!")


if __name__ == "__main__":
    demo_stevens_power_law()
    demo_vestibular_integration()
    demo_poisson_detection()
    demo_von_mises_stress()
    demo_propagation()
    demo_impedance_matching()
    demo_complete_pipeline()
    print("\n" + "=" * 70)
    print("[DONE] Universal Sensor Translation complete!")
    print("=" * 70)
