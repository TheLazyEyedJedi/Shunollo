"""
example_flow_analysis.py
------------------------
Using VascularAnalyzer for Network Anomaly Detection

This example shows how to use the flow topology analyzer to detect:
1. Resonance Cascade (mesh topology)
2. System degradation (increasing resistance)
3. Flow imbalance (throughput/latency mismatch)

Domain: DevOps / Network Security
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from shunollo_core.physics_flow import VascularAnalyzer


def simulate_network_surge():
    """Demonstrate DDoS detection via topology analysis."""
    print("=" * 60)
    print("SCENARIO: Detecting Resonance Cascade via Topology Analysis")
    print("=" * 60)
    
    analyzer = VascularAnalyzer()
    
    # Normal tree topology (load balancer -> servers)
    print("\n[NORMAL] Tree topology: 1 source -> 5 sinks, 5 edges")
    is_anomaly, turbulence = analyzer.detect_topology_anomaly(
        sources=1, sinks=5, edges=5
    )
    print(f"  Anomaly: {is_anomaly}, Turbulence: {turbulence:.2f}")
    
    # DDoS: Many sources hitting one target
    print("\n[EVENT] Amplification surge: 100 sources -> 1 sink, 100 edges")
    is_anomaly, turbulence = analyzer.detect_topology_anomaly(
        sources=100, sinks=1, edges=100
    )
    print(f"  Anomaly: {is_anomaly}, Turbulence: {turbulence:.2f}")
    
    # Reflection surge: mesh topology
    print("\n[EVENT] Reflection surge: 20 nodes, 50 edges (mesh)")
    is_anomaly, turbulence = analyzer.detect_topology_anomaly(
        sources=10, sinks=10, edges=50
    )
    print(f"  Anomaly: {is_anomaly}, Turbulence: {turbulence:.2f}")


def simulate_system_degradation():
    """Demonstrate resistance trend detection."""
    print("\n" + "=" * 60)
    print("SCENARIO: Detecting Memory Leak via Resistance Trend")
    print("=" * 60)
    
    analyzer = VascularAnalyzer()
    
    # Simulate healthy system
    print("\n[HEALTHY] Stable throughput, stable latency")
    for i in range(5):
        r = analyzer.calculate_configurational_resistance(
            queue_depth=10,
            cpu_load=0.5,
            throughput_bps=1000
        )
        print(f"  Sample {i+1}: R = {r:.6f}")
    
    is_increasing, slope = analyzer.check_resistance_trend()
    print(f"  Resistance increasing: {is_increasing}, slope: {slope:.8f}")
    
    # Simulate memory leak (queue growing, throughput dropping)
    analyzer.reset()
    print("\n[DEGRADING] Queue growing, throughput dropping (memory leak)")
    for i in range(5):
        r = analyzer.calculate_configurational_resistance(
            queue_depth=10 + i * 50,      # Queue growing
            cpu_load=0.5 + i * 0.1,       # CPU increasing
            throughput_bps=1000 - i * 100  # Throughput dropping
        )
        print(f"  Sample {i+1}: R = {r:.6f}")
    
    is_increasing, slope = analyzer.check_resistance_trend()
    print(f"  Resistance increasing: {is_increasing}, slope: {slope:.8f}")
    if is_increasing:
        print("  [!] WARNING: System degradation detected!")


def simulate_flow_imbalance():
    """Demonstrate flow imbalance detection."""
    print("\n" + "=" * 60)
    print("SCENARIO: Detecting Backend Bottleneck via Flow Imbalance")
    print("=" * 60)
    
    analyzer = VascularAnalyzer(
        baseline_bytes=1000,
        baseline_latency=100
    )
    
    # Healthy system: high throughput, proportional latency
    print("\n[HEALTHY] High throughput, low latency")
    for _ in range(5):
        imbalance = analyzer.calculate_flow_imbalance(
            bytes_out=5000,
            latency_ms=50
        )
    mean_imbalance = analyzer.get_mean_imbalance()
    print(f"  Mean imbalance: {mean_imbalance:.4f}")
    
    # Bottleneck: high throughput but high latency (database lock)
    analyzer.reset()
    print("\n[BOTTLENECK] High throughput but high latency (database lock)")
    for _ in range(5):
        imbalance = analyzer.calculate_flow_imbalance(
            bytes_out=5000,
            latency_ms=2000  # 2 second latency!
        )
    mean_imbalance = analyzer.get_mean_imbalance()
    print(f"  Mean imbalance: {mean_imbalance:.4f}")
    if mean_imbalance > 1.0:
        print("  [!] WARNING: Flow imbalance detected! Check database connections.")


if __name__ == "__main__":
    simulate_network_surge()
    simulate_system_degradation()
    simulate_flow_imbalance()
    print("\n[DONE] Flow analysis example complete!")
