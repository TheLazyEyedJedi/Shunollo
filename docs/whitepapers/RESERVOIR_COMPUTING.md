# Reservoir Computing
**Subject**: Architectural Justification for Echo State Networks (ESN)

## The Problem with Transformers
Traditional Large Language Models (Transformers) are unsuitable for real-time anomaly detection:

1.  **Memory**: A 7B parameter model requires >14GB of RAM.
2.  **Compute**: Inference is GPU-bound, requiring cloud infrastructure.
3.  **High Latency**: Token-by-token generation is too slow for microsecond decision-making.

## The Solution: The Digital Cortex
Shunollo uses a **Reservoir Computer** (specifically an Echo State Network) as its core "Intuition".

### How it Works
1.  **The Reservoir (Liquid State)**:
    *   A fixed, randomly-connected recurrent network of ~500 neurons.
    *   Input signals "perturb" the liquid, creating a high-dimensional temporal echo.
    *   The reservoir is **never trained**—its chaos is its power.

2.  **The Readout (Cortex)**:
    *   A simple linear layer that reads the reservoir's final state.
    *   Only this layer is trained, via cheap **Ridge Regression**, not Backprop.

### Why This is Better for Real-Time Systems
*   **Memory**: ~2MB per model.
*   **Compute**: CPU-only. No GPU required.
*   **Training Time**: < 1ms per sample.

## Conclusion
Shunollo rejects the "Bigger is Better" dogma of modern AI. By using Reservoir Computing, we achieve "Tiny AI" that can live inside edge devices, feeling the flow of data like a nervous system.

---
*© Shunollo Labs | Based on work by Jaeger (2001)*
