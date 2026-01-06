# Neural Dissonance
**Subject**: The Physics of "Gut Feeling"

## The Problem: Multi-Modal Integration
How does the brain combine 8+ senses into a single "feeling" of danger?

**Answer**: Dissonance.

## The Dissonance Score
Shunollo computes a **Dissonance Score** by measuring the *disagreement* between sensory channels:

$$D = \sigma(\text{SensoryVector})$$

Where $\sigma$ is the standard deviation across the 13-dimensional somatic vector.

### Interpretation
1.  **Low Dissonance ($D \approx 0$)**: All senses agree. The signal is coherent. Either "all normal" or "all anomalous."
2.  **High Dissonance ($D > 0.3$)**: Senses disagree. Something is *inconsistent*. This is a "Gut Feeling" of wrongness.
3.  **Base Rate Awareness**: Accounts for the fact that most data is benign, preventing over-sensitivity in low-noise environments.

## The Bayesian Referee
The Dissonance Score is fed to the **Pre-Frontal Cortex** (the Agent), which uses it as a prior for decision-making.

*   High Dissonance + One Anomalous Sense → Investigate.
*   Low Dissonance + All Normal → Ignore.

## Conclusion
Shunollo's "Gut Feeling" is mathematically grounded in the physics of sensory disagreement. It's not magic—it's variance.

---
*© Shunollo Labs*
