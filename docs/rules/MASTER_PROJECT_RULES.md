# Shunollo Master Project Rules

> **Goal**: Absolute Isomorphism between Human Neuroanatomy and AI Architecture.
> **Philosophy**: The Code *is* the Anatomy.

## 1. Architectural Integrity (The Schism)
*   **Core vs Applications**: `shunollo_core` (Brain) must NEVER import from applications (Body).
    *   **Core**: Pure math/physics, framework agnostic.
    *   **Apps**: Workers, Routers, UI.
*   **Data Decoupling**: Applications must have their own data directories. Never access `../shunollo_core/data` at runtime.

## 2. Operational Standards
*   **Feedback Loops**: Use environment flags to prevent recursive processing loops.
*   **Race Conditions**: Test harnesses must poll the Thalamic bus for queue completion, not just process exit.

## 3. Sensory Protocols (The Codex)
All new features must adhere to this isomorphic mapping:

| Biological | Cybernetic (Metric) | Interpretation |
|---|---|---|
| **Sight (Brightness)** | Magnitude | Size / Volume / Saliency |
| **Roughness** | Entropy | Information Density |
| **Temperature** | Volatility | Rate of Change / Flux |
| **Vibration** | Jitter | Inter-arrival Time Variance |
| **Muscle Stretch** | System Load | Resource Utilization |
| **Tension** | Queue Depth | Backpressure |
| **Kinesthesia** | Velocity | Throughput |
| **Balance** | Stability | State Consistency |
| **Acceleration** | Burstiness | Sudden Spikes |
| **Pain** | Error Rate | Failures |
| **Taste (Sweet)** | Valid Syntax | Structured Data |
| **Taste (Bitter)** | Malformed | Invalid Data |
| **Taste (Sour)** | Corruption | Broken Data |

## 4. Deployment Checklist
1.  **Check Infrastructure**: Are dependencies (e.g., Redis) running?
2.  **Verify Backend**: Is the API port responsive?
3.  **Run Tests**: `pytest tests/`
