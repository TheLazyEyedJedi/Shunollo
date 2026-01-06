# Sensory Lexicon
## The Vocabulary of Digital Sensation

This document defines the sensory vocabulary used by Shunollo to describe data.

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

## Universal Application
These senses apply across domains:
- **Finance**: Market volatility as "temperature"
- **Healthcare**: Patient vitals as "roughness"
- **DevOps**: Server load as "muscle stretch"
- **IoT**: Sensor readings as "flux"
