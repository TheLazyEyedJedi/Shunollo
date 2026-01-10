# Autoencoder Imagination
**Subject**: Detecting the Unknown via Reconstruction Error

## The Problem: Unknown Unknowns
Supervised learning requires labeled data. But how do you label something you've never seen?

**The Solution**: Don't classify—**Imagine**.

## The Autoencoder as a Memory Palace
An Autoencoder is a neural network that learns to compress and reconstruct its input.

```
Input (18-dim) -> [Encoder] -> Latent (6-dim) -> [Decoder] -> Output (18-dim)
```

If the network is trained **only on normal data**, it learns the "structure of normality."

### The Anomaly Test
When a new signal arrives:
1.  Compress it to the latent space.
2.  Reconstruct it from the latent space.
3.  Measure the **Reconstruction Error** ($MSE$).

If the signal is "normal," the Autoencoder can imagine it perfectly ($MSE \approx 0$).
If the signal is "anomalous," the Autoencoder **fails to imagine it** ($MSE \uparrow$).

### The Training Protocol
1.  **Infancy (Random)**: Initialize weights randomly.
2.  **Childhood**: Feed 100-1000 "Normal" samples. Minimize Reconstruction Error.
3.  **Adulthood (Deployment)**: Test new samples. Anomalies are signals that "can't be imagined."

This forces the AI to learn the "Essential Structure" of normal data, discarding noise.

## Conclusion
The Autoencoder gives Shunollo "Imagination." It can recognize an anomaly not by what it *is*, but by its inability to *conceive* of it. This is the closest we have come to AI "Surprise."

---
*© Shunollo Labs | Based on work by Kingma & Welling (2013)*
