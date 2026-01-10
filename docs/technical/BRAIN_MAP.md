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
| **Hippocampus** | `shunollo_core/memory/hippocampus.py` | Episodic Memory (Physics-RAG) |
| **Amygdala** | Physics Engine | Danger Assessment (Fear) |
| **RAS (Reticular Activating System)** | `shunollo_core/subcortex/ras.py` | Attention Gating |

### 2.1 RAS (Reticular Activating System)
*   **Human**: Filters sensory input to prevent brain overload.
*   **Shunollo**: Filters out background noise so the Brain isn't overwhelmed.
*   **Logic**: Low-salience signals are dropped. High-salience signals are promoted.

### 2.2 Hippocampus (Integrated in v0.3.7) 🆕
*   **Human**: Consolidates short-term memory to long-term. Enables "Déjà Vu."
*   **Shunollo**: Stores sensory episodes as 18-dim physics vectors. Enables similarity search.
*   **Logic**: `recall_similar()` queries past experiences. `get_novelty_score()` measures surprise.

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
Raw Data -> Transducer -> Physics Engine -> Somatic Vector -> Hippocampus -> Brain -> Decision
                                                    ↑                           |
                                                    └───── Déjà Vu (Recall) ────┘
```

### B. The Somatic Vector (18 Dimensions)

| Index | Field | Metric | Normalized Range |
|---|---|---|---|
| 0 | Energy | Kinetic Impact | 0-10 |
| 1 | Entropy | Information Density | 0-8 bits |
| 2 | Frequency | Rate | 0-1000 Hz |
| 3 | Roughness | Texture | 0-1 |
| 4 | Viscosity | Flow Resistance | 0-1 |
| 5 | Volatility | Standard Deviation | 0-1 |
| 6 | Action | Lagrangian Integral | 0-10 |
| 7 | Hamiltonian | Total Energy | 0-10 |
| 8 | EWR | Entropy-to-Wait Ratio | 0-10 |
| 9 | Hue | Color Spectrum | 0-1 |
| 10 | Saturation | Color Purity | 0-1 |
| 11 | Pan | Stereo Position | -1 to 1 |
| 12 | Spatial X | 3D Position X | -1 to 1 |
| 13 | Spatial Y | 3D Position Y | -1 to 1 |
| 14 | Spatial Z | 3D Position Z | -1 to 1 |
| 15 | Harmony | Spectral Coherence | 0-1 |
| 16 | Flux | Rate of Change | 0-10 |
| 17 | Dissonance | Sensory Disagreement | 0-1 |

### C. Physics-RAG Flow

```python
# Perception with Memory
signal = sense(data)                          # Create 18-dim vector
priors = hippocampus.recall_similar(signal)   # Query: "Have I felt this before?"
decision = agent.decide(signal, priors)       # Act with context
hippocampus.remember(signal)                  # Consolidate if novel
```
