# The Machine Imagination: Anomaly via Reconstruction
**Date**: 2026-01-06
**Subject**: Unsupervised Anomaly Detection using Autoencoders

## 1. The Philosophy of "Alien"
How do you detect a threat you have never seen before (Zero-Day)?
You cannot use a Classifier (Supervised Learning) because you have no labels.
You must use **Imagination**.

*   **Premise**: If the AI can "Imagine" (Reconstruct) the input, it is Normal.
*   **Premise**: If the AI *fails* to Imagine the input, it is Alien.

## 2. The Architecture: Autoencoder
Shunollo implements a classic bottleneck Autoencoder:

### 2.1 The Encoder (Compression)
$$z = \sigma(W_{enc} \cdot x + b)$$
Compresses the 13-dimensional Physics Vector ($x$) into a 4-dimensional Latent Space ($z$).
This forces the AI to learn the "Essential Structure" of normal traffic, discarding noise.

### 2.2 The Decoder (Reconstruction)
$$\hat{x} = \sigma(W_{dec} \cdot z + b)$$
Attempts to recreate the original input from the compressed memory.

## 3. The Metric: Surprise (Reconstruction Error)
We define "Surprise" as the Mean Squared Error (MSE) between reality and imagination:

$$Surprise = ||x - \hat{x}||^2$$

*   **Scenario A (Normal HTTP)**: The AI has seen HTTP before. It effectively compresses and decompresses it. $Surprise \approx 0.1$.
*   **Scenario B (Exfiltration Tunnel)**: The AI has never seen this high-entropy, low-jitter pattern. It fails to compress it efficiently. The reconstruction is blurry. $Surprise \rightarrow 1.0$.

## 4. The "Childhood" (Baseline Training)
To work, the Autoencoder must have a "Childhood"—a period of training on known-safe data (Baseline).
1.  **Initialize**: Random Weights (Tabula Rasa).
2.  **Childhood**: Feed 100-1000 "Normal" packets. Minimise Reconstruction Error.
3.  **Adulthood**: Freeze weights (or slow learn). Monitor Surprise.

## 5. Conclusion
This component gives Shunollo the ability to feel **Confusion**.
When `Surprise > Threshold`, the system is not saying "This is Malware." It is saying "I don't understand this." In high-security environments, unexplained phenomena constitute a threat.
