# Adversarial Review: Senior Neuroscientist (Round 2)
**Role:** Computational Neuroscientist / Biologist
**Persona:** "The Purist"
**Date:** 2026-01-09
**Status:** 🟠 SKEPTICAL OPTIMISM

## "You have the parts, but not the cycle."

The Developer complains about performance. I complain about **Plausibility**.
You are trying to run `FactorGraph.optimize()` in real-time. Do you know what happens if a brain tries to rewire its entire long-term memory while simultaneously processing visual input?
**Seizures.** Or at best, hallucination.

### 1. The Missing Circadian Rhythm (Sleep)
Biology separates **Acquisition** (Wake) from **Consolidation** (Sleep).
*   **Wake**: Fast, local Hebbian updates. `FactorGraph.add_node()`.
*   **Sleep**: Slow, global optimization. `FactorGraph.optimize()`.
    *   This is **Hippocampal Replay** (Sharp-Wave Ripples).
    *   The brain "replays" the day's events 20x faster during sleep to minimize the free energy of the internal model.

**Critique**: Your agent is an insomniac. It tries to "solve" its memory instantly. It will be unstable.

### 2. Dopamine is Missing (Precision Dynamics)
In `active_inference.py`:
```python
self.precision = 1.0 / (prediction_error + 0.1)
```
This is mathematically correct for a Kalman Filter, but biologically wrong.
Precision ($\Pi$) is encoded by **Neuromodulators** (Dopamine, Acetylcholine). These don't change instantly. They have:
*   **Tonic Levels**: Baseline attention (Mood).
*   **Phasic Bursts**: Instant reaction to surprise.
*   **Decay**: They dissipate over time.

Your agent has "Perfect Attention" every millisecond. It lacks the concept of "Boredom" (Habituation) or "Hyper-focus" (Flow State).

### 3. Foveated Rendering
The `DistortionModel` is a good start ("Brown-Conrady"), but you are applying it like a static camera lens.
Biological eyes move (Saccades). Computation is only expensive at the Fovea (Center).
*   **Peripheral Vision**: High distortion, Low Resolution, High Temporal Sensitivity (Motion).
*   **Para-Foveal**: Medium distortion.
*   **Foveal**: Zero distortion, High Resolution.

Your model distorts the data, but does it reduce the *computational load* of the distorted parts? If not, it's just a filter, not an optimization.

---

## 🛠 Actionable Demands

1.  **Implement Sleep Mode**:
    *   Store raw events in a "Hippocampus" buffer during the day (Wake).
    *   Trigger `optimize()` only when input flow stops ("Sleep").
    *   This satisfies the Developer's performance constraint too.

2.  **Add Tonic/Phasic Precision**:
    *   Add a decay factor to `self.precision`.
    *   `self.precision = self.precision * 0.9 + new_precision * 0.1`.
    *   This simulates the metabolic half-life of neurotransmitters.

3.  **Active Saccades**:
    *   The `DistortionModel` should define *where* the agent looks (Center Index).
    *   The agent must *choose* to move this center (Action).

**Verdict**: ⚠️ CONDITIONAL PASS. You must respect the Sleep Cycle.
