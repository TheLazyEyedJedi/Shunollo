# Brain Map
## Anatomical Reference for the Isomorphic Architecture

This document maps Shunollo's code to biological brain structures.

---

## 1. The Sensory Cortex (Input Layer)

| Biological Region | Shunollo Module | Function |
|---|---|---|
| **Visual Cortex** | `shunollo_core/perception/visual_cortex.py` | Color/Pattern Recognition |
| **Auditory Cortex** | `shunollo_core/perception/auditory_cortex.py` | Rhythm/Spectral Analysis |
| **Somatosensory Cortex** | Transducers (Application Layer) | Signal -> Physics Transduction |
| **Gustatory Cortex** | `shunollo_core/perception/gustatory_cortex.py` | Data Validity (Sweet/Bitter) |
| **Olfactory Bulb** | `shunollo_core/perception/olfactory_bulb.py` | Pattern Matching |

---

## 2. The Subcortex (Processing Layer)

| Biological Region | Shunollo Module | Function |
|---|---|---|
| **Thalamus** | `shunollo_runtime/thalamus.py` | Central Message Bus |
| **Hippocampus** | `shunollo_core/memory/hippocampus.py` | Episodic Memory Storage |
| **Amygdala** | Physics Engine | Threat Assessment (Fear) |
| **RAS (Reticular Activating System)** | `shunollo_core/subcortex/ras.py` | Attention Gating |

### 2.1 RAS (Reticular Activating System)
*   **Human**: Filters sensory input to prevent brain overload.
*   **Shunollo**: Filters out background noise so the Brain isn't overwhelmed.
*   **Logic**: Low-salience signals are dropped. High-salience signals are promoted.

---

## 3. The Pre-Frontal Cortex (Decision Layer)

| Biological Region | Shunollo Module | Function |
|---|---|---|
| **Broca's Area** | `shunollo_core/cognition/brocas_area.py` | Output Formatting |
| **Wernicke's Area** | `shunollo_core/cognition/wernickes_area.py` | Input Comprehension |
| **Motor Cortex** | `shunollo_core/motor/motor_cortex.py` | Action Execution |

---

## 4. The Anatomy of a Signal

### A. The Signal Lifecycle
```
Raw Data -> Transducer -> Physics Engine -> Somatic Vector -> Brain -> Decision
```

### B. The Somatic Vector (13 Dimensions)
| Index | Sense | Metric |
|---|---|---|
| 0 | Energy | Kinetic Impact |
| 1 | Roughness | Entropy |
| 2 | Flux | Rate of Change |
| 3 | Viscosity | Resistance |
| 4 | Harmony | Spectral Coherence |
| 5 | Dissonance | Sensory Disagreement |
| 6 | Volatility | Standard Deviation |
| 7 | Action | Lagrangian Integral |
| 8 | Hamiltonian | Total Energy |
| 9 | EWR | Entropy-to-Wait Ratio |
| 10 | Stochastic Drift | Random Walk Violation |
| 11 | Salience | Importance Score |
| 12 | Classification | Binary (0/1) |
