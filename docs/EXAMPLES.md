# Shunollo Core Examples
**"The Isomorphic Engine"**

Shunollo is a Universal Anomaly Detection system. It does not use rules or signatures. Instead, it measures the **Physics of Information**.
This folder contains 4 "Bare Bones" examples demonstrating how to apply Shunollo to entirely different industries without changing a single line of core code.

## 1. Finance (`market_sense.py`)
**Goal**: Detect Market Manipulation ("Pump and Dump") vs Efficient Markets.
*   **Physics Mapping**:
    *   **Energy ($E$)** $\rightarrow$ Price Delta $\times$ Volume (Magnitude of Move)
    *   **Roughness ($R$)** $\rightarrow$ Volatility (Texture of the chart)
    *   **Flux ($\Phi$)** $\rightarrow$ Tick Rate Variance (Panic)
*   **Result**: Efficient markets feel "Smooth" (Random Walk). Manipulation feels "Rough" (Non-Random).
*   **Run**: `python examples/market_sense.py`

## 2. Health (`bio_rhythm.py`)
**Goal**: Detect Atrial Fibrillation (AFib) vs Healthy Sinus Rhythm.
*   **Physics Mapping**:
    *   **Entropy ($H$)** $\rightarrow$ Heart Rate Variability (Complexity)
        *   *Note: Healthy hearts have HIGH entropy (complex). Dead hearts have LOW entropy (flat).*
    *   **Flux ($\Phi$)** $\rightarrow$ R-R Interval Jitter (Instability)
*   **Result**: AFib creates a "Super-Entropic" state of pure chaos (High Flux) that the brain flags as an anomaly.
*   **Run**: `python examples/bio_rhythm.py`

## 3. DevOps (`server_heat.py`)
**Goal**: Distinguish "Meltdown" (Deadlock) from "Black Friday" (Efficient Scaling).
*   **Physics Mapping**:
    *   **Action ($S$)** $\rightarrow$ CPU Load (Work being done)
    *   **Viscosity ($\eta$)** $\rightarrow$ Latency (Friction/Resistance)
    *   **Lagrangian Strain** $\rightarrow$ Action $\times$ Viscosity
        *   *High Action + Low Viscosity = Efficiency (Good)*
        *   *High Action + High Viscosity = Thrashing (Bad)*
*   **Result**: The brain learns that high load is safe *only* if latency remains low.
*   **Run**: `python examples/server_heat.py`

## 4. IoT / Manufacturing (`motor_decay.py`)
**Goal**: Detect Ball Bearing Failure in industrial motors.
*   **Physics Mapping**:
    *   **Roughness ($R$)** $\rightarrow$ Vibration G-Force Texture
    *   **Energy ($E$)** $\rightarrow$ RPM (Rotational Kinetic Energy)
*   **Result**: As bearings degrade, they introduce "Grit" (High Frequency Roughness). Shunollo detects this textual change long before the motor overheats.
*   **Run**: `python examples/motor_decay.py`

## 5. Universal Sensor Translator (`universal_sensor.py`) 🆕 (v0.3.7)
**Goal**: Demonstrate how **ANY** data source can be bolted onto Shunollo.
*   **Physics Mapping**:
    *   **Stevens' Power Law**: Perceptual scaling (e.g. Pain exponent for Errors).
    *   **Vestibular Integration**: Rate-to-State conversion for sustained loads (e.g., fluid momentum).
    *   **Poisson Statistics**: Quantum-limited detection of faint anomalies (e.g., sensor drift).
*   **Result**: A complete pipeline transforming raw numbers (Temp, Pressure, Light) into AI sensations (Burn, Strain, Dazzle).
*   **Run**: `python examples/universal_sensor.py`

---

## How it Works (The Code)
All examples follow the same 3-step pattern:

1.  **Sense**: Convert domain data (Price, Heartbeat, CPU) into a **Physics Profile**.
2.  **Vectorize**: Use `signal.to_vector(normalize=True)` to create an **18-dimensional** Somatic Vector.
3.  **Intuit**: Feed the vector to the neural cortex to get an Anomaly Score (0.0 - 1.0).

This proves that **Code is Anatomy**. The same mathematical structures that protect a network can protect a heart.

---

## Physics-RAG: Memory-Augmented Detection (Integrated in v0.3.7) 🆕

All examples can now leverage **episodic memory** for One-Shot Learning:

```python
from shunollo_core.memory.hippocampus import Hippocampus

hippo = Hippocampus()

# After detecting an anomaly, store it
hippo.remember(signal)

# On next run, check if we've seen this before
priors = hippo.recall_similar(new_signal.to_vector(), k=3)
if priors:
    print(f"Déjà Vu! This matches incident from {priors[0][0].timestamp}")
```

This enables:
- **Zero-training recognition** of previously-seen patterns
- **Novelty detection** via `get_novelty_score()`
- **Faster anomaly response** on repeat occurrences
