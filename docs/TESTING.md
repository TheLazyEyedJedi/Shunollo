# Shunollo Testing Strategy
**Last Updated**: 2026-01-09
**Coverage**: 204 Tests (196 Unit, 8 Integration)

## 1. Philosophy: "Trust but Verify the Physics"

Shunollo is a **Mathematical Engine**. Unlike traditional software where "it works if it doesn't crash," Shunollo works only if the mathematics are physically and biologically correct.

Our testing strategy focuses on three pillars:
1.  **Mathematical Correctness**: Do the equations (Entropy, Von Mises, Stevens' Law) match their academic definitions?
2.  **Biological Plausibility**: Does the system behave like a nervous system? (e.g., Sensory adaptation, Homeostasis).
3.  **Architectural Stability**: Do the loosely coupled components (Physics $\to$ Sensation $\to$ Perception $\to$ Cognition) integrate without data loss?

---

## 2. Test Structure

Tests are located in the `tests/` directory and mirror the core architecture.

| Test Category | File | Description |
| :--- | :--- | :--- |
| **Foundations** | `test_physics_flow.py` | Core metric calculations (Entropy, Flux, Roughness). |
| **Advanced Physics** | `test_advanced_physics.py` | **Phase 500**: Psychophysics, Vestibular, Poisson, Von Mises. |
| **Cognition** | `test_active_inference.py` | Free Energy Principle, Belief Updating, Surprise minimization. |
| **Memory** | `test_physics_rag.py` | Physics-RAG, Vector retrieval, Episodic memory. |
| **Holographic** | `test_holographic.py` | Fourier Holographic Associative Memory (F-HAM). |
| **Perception** | `test_stochastic_resonance.py` | Signal detection in noise (Dithering). |
| **Pattern Search** | `test_spade.py` | SPADE (Hermite-Gaussian pattern mining). |
| **Neural Net** | `test_neural_net.py` | Echo State Network (Reservoir) dynamics. |
| **Integration** | `test_integration_math.py` | Full pipeline tests (Sensor $\to$ Brain). |

---

## 3. How to Run Tests

### Standard Run (All Tests)
```bash
python -m pytest tests/
```

### Verbose Run (See all pass/fail)
```bash
python -m pytest tests/ -v
```

### Stop on First Failure (Debugging)
```bash
python -m pytest tests/ -x
```

### Run Specific Category
```bash
python -m pytest tests/test_advanced_physics.py
```

---

## 4. Key Validation Areas

### 4.1 Advanced Physics (Phase 500)
Verified in `test_advanced_physics.py`:
*   **Stevens' Power Law**: Confirms that 5% signal increase $\neq$ 5% sensation increase. (e.g., Pain scales exponentially).
*   **Vestibular Dynamics**: Confirms that rapid acceleration inputs integrate into a sustained "velocity" state (simulating dizziness/alertness).
*   **Poisson Statistics**: Confirms detection probability drops correctly as signal approaches the noise floor (Quantum limit).
*   **Von Mises Stress**: Confirms that asymmetric system loads (bottlenecks) trigger alerts while uniform high loads do not.

### 4.2 Cognitive Engine
Verified in `test_active_inference.py`:
*   **Surprise Minimization**: Agents actively update beliefs to minimize prediction error.
*   **Precision Weighting**: Agents ignore noisy signals (low precision) and focus on reliable ones.

### 4.3 Holographic Memory
Verified in `test_holographic.py`:
*   **Superposition**: Multiple signals can be stored in the same complex encoding.
*   **Associative Recall**: A partial cue retrieves the full original pattern.

---

## 5. Adding New Tests

When adding a new physics module (e.g., `NewForce.py`):
1.  Create `tests/test_new_force.py`.
2.  **Zero-Value Test**: What happens at 0 input? (Should be 0 energy).
3.  **Linearity Test**: If I double input, does output double? (Or follow Power Law?).
4.  **Boundary Test**: What happens at `math.inf` or `NaN`?
5.  **Integration Test**: Create a scenario in `test_integration_math.py` combining it with existing senses.

---

## 6. Current Status (v0.2.0)

*   **Total Tests**: 176
*   **Result**: 100% Passing
*   **Known Flaky Tests**: None (Fixed in Phase 3).

*Authorized by Shunollo Core Team.*
