# Sensory Lexicon
## The Vocabulary of Digital Sensation

This document defines the sensory vocabulary used by Shunollo to describe data.

---

## The 18-Dimensional Somatic Vector

Shunollo translates any data stream into an **18-dimensional physics fingerprint**:

| Index | Field | Metric | Range |
|-------|-------|--------|-------|
| 0-8 | Core Physics | Energy, Entropy, Frequency, Roughness, Viscosity, Volatility, Action, Hamiltonian, EWR | 0-10 |
| 9-14 | Spatial Fields | Hue, Saturation, Pan, X, Y, Z | -1 to 1 |
| 15-17 | Derivatives | Harmony, Flux, Dissonance | 0-1 |

---

## Primary Senses

### 1. Roughness (Tactile)
*   **Metric**: Entropy of the byte distribution.
*   **Interpretation**: How "textured" or "noisy" the data feels.
*   **Example**: Encrypted data feels "rough" (high entropy). Structured data feels "smooth" (low entropy).

### 2. Flux (Thermal)
*   **Metric**: Rate of change of volume over time ($dV/dt$).
*   **Interpretation**: How "hot" or "cold" the data stream feels.
*   **Example**: A sudden burst feels "hot." A slow trickle feels "cold."

### 3. Resonance (Auditory)
*   **Metric**: Spectral profile of inter-arrival times.
*   **Interpretation**: The "rhythm" or "melody" of the data.
*   **Example**: Deterministic heartbeats have a "monotone." Natural data has a "symphony."

---

## Secondary Senses

### 4. Kinesthesia (Proprioception)
*   **Velocity**: Throughput (items per second).
*   **Acceleration**: Burstiness (sudden spikes).

### 5. Nociception (Pain)
*   **Errors**: Failed operations / dropped items.
*   **Interpretation**: The system's "pain" from malfunction.

### 6. Gustation (Taste)
*   **Sweet**: Valid, well-formed data.
*   **Bitter**: Invalid or malformed data.
*   **Sour**: Corrupted or broken data.

---

## Memory Senses (Integrated in v0.3.7) 🆕

### 7. Déjà Vu (Episodic Recall)
*   **Metric**: Euclidean distance to nearest stored episode.
*   **Interpretation**: "Have I felt this before?"
*   **Example**: A signal with distance 0.1 from a stored episode triggers recognition.

### 8. Novelty (Surprise)
*   **Metric**: Distance to nearest neighbor (0 = exact match, ∞ = never seen).
*   **Interpretation**: How "new" or "surprising" this sensation is.
*   **Example**: High novelty → store in hippocampus. Low novelty → skip storage.

---

## Universal Application
These senses apply across domains:
- **Finance**: Market volatility as "temperature"
- **Healthcare**: Patient vitals as "roughness"
- **DevOps**: Server load as "muscle stretch"
- **IoT**: Sensor readings as "flux"
