# Physics-RAG: Retrieval-Augmented Generation for Sensation

**"Memory is not optional. Perception is always filtered through experience."**

---

## Abstract

Physics-RAG introduces episodic memory into Shunollo's cognitive architecture, enabling AI systems to recognize previously-encountered sensory patterns without explicit signature matching. By storing and querying 18-dimensional physics vectors, agents can experience "Déjà Vu" — instant recognition of familiar sensory textures.

---

## 1. The Biological Inspiration

### 1.1 The Problem with Amnesia

Traditional anomaly detection systems are *amnesiac*: they process each input in isolation, with no memory of what they have "felt" before. This forces them to:
- Rely on pre-trained models (stale knowledge)
- Require explicit signatures (brittle matching)
- Miss one-shot learning opportunities

### 1.2 How Biology Solves It

The human hippocampus provides:
- **Episodic Memory**: Storage of individual experiences with spatiotemporal context
- **Pattern Completion**: Recognition from partial matches
- **Consolidation Gating**: Only "important" experiences are stored (salience filtering)

Shunollo's Hippocampus module mirrors this architecture.

---

## 2. The Physics-RAG Architecture

### 2.1 Vector Representation

Every sensory experience is encoded as an **24-dimensional normalized vector** (Updated Phase 500):

```
[energy, entropy, frequency, roughness, viscosity, volatility, 
 action, hamiltonian, ewr, hue, saturation, pan, 
 spatial_x, spatial_y, spatial_z, harmony, flux, dissonance,
 distortion, volume_log, intensity_log, velocity, strain, resonance]
```

Each dimension is normalized to `[0, 1]` range for fair distance comparison.

### 2.2 The Recall Loop

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│   PERCEIVE   │ --> │    RECALL     │ --> │    DECIDE    │
│ (18-dim vec) │     │  (Déjà Vu?)   │     │ (with prior) │
└──────────────┘     └───────────────┘     └──────────────┘
                            │
                            v
                     ┌───────────────┐
                     │  CONSOLIDATE  │
                     │ (if novel)    │
                     └───────────────┘
```

### 2.3 Similarity Metric

Episodes are matched using **Euclidean distance** in normalized space:

$$d(p, q) = \sqrt{\sum_{i=1}^{18}(p_i - q_i)^2}$$

Where:
- `d < 0.5` = Very similar (strong Déjà Vu)
- `d < 1.0` = Somewhat similar (weak Déjà Vu)
- `d > 1.0` = Novel (no match)

---

## 3. Why Vector Size Matters

### 3.1 The "Boring Winner" Advantage

| System | Vector Size | Compute | Storage | Latency |
|--------|-------------|---------|---------|---------|
| OpenAI Embeddings | 1,536-dim | GPU/API | Vector DB | 200ms+ |
| **Physics-RAG** | **18-dim** | **CPU** | **SQLite** | **<1ms** |

Physics-RAG achieves real-time recall because:
- 18 floats fit in a CPU cache line
- Euclidean distance is trivial math
- No external dependencies required

### 3.2 Why 18 Dimensions?

Each dimension represents a *universal physical property*:
- **Not domain-specific** (works for finance, health, IoT)
- **Not learned** (computed from first principles)
- **Physically meaningful** (can be interpreted by humans)

---

## 4. One-Shot Learning

### 4.1 The Use Case

1. **Day 1**: Novel anomaly detected → Agent flags it → Human labels it "Malicious" → Stored in hippocampus
2. **Day 2**: Same sensory texture appears → `recall_similar()` fires → Instant recognition

No retraining. No signature updates. Just **sensory memory**.

### 4.2 The Novelty Score

```python
novelty = hippocampus.get_novelty_score(signal.to_vector())
if novelty > 1.0:
    print("Novel pattern - storing...")
    hippocampus.remember(signal)
```

The novelty score is the distance to the nearest stored episode. High novelty indicates a never-before-seen sensation.

---

## 5. Storage Strategy

### 5.1 JSONL Append-Only Log

Episodes are stored as JSON Lines:
```json
{"energy": 0.5, "entropy": 0.8, "roughness": 0.3, ..., "timestamp": "2026-01-07T12:00:00Z"}
```

Benefits:
- Human-readable for debugging
- Append-only for write safety
- Easy migration to SQLite if needed

### 5.2 In-Memory Caching

To avoid O(n) file reads on every query:
- Episodes are loaded into memory once
- Cache is invalidated on write
- Max cache size configurable (default: 10,000 episodes)

---

## 6. Future Work: Salience Gating

The current implementation stores all remembered signals. Future versions may implement **Salience Gating**:

- **Novelty Gate**: Store only if `novelty > threshold`
- **Intensity Gate**: Store only if `energy > 90th percentile`
- **Feedback Gate**: Store only if agent explicitly flags importance

This prevents memory bloat while preserving meaningful experiences.

---

## 7. Conclusion

Physics-RAG transforms Shunollo from a stateless physics calculator into a cognitive architecture with episodic memory. By encoding experiences as 18-dimensional physics vectors and enabling fast similarity search, agents can recognize previously-encountered patterns instantly — enabling true One-Shot Learning without retraining.

---

## References

1. Eichenbaum, H. (2017). "Memory: Organization and Control." Annual Review of Psychology.
2. Hopfield, J.J. (1982). "Neural Networks and Physical Systems with Emergent Collective Computational Abilities."
3. Lewis-Peacock, J.A. & Norman, K.A. (2014). "Competition between items in working memory leads to forgetting."
