# Shunollo - The Biomimetic Physics Engine

[![PyPI version](https://img.shields.io/pypi/v/shunollo.svg)](https://pypi.org/project/shunollo/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/TheLazyEyedJedi/Shunollo/actions/workflows/ci.yml/badge.svg)](https://github.com/TheLazyEyedJedi/Shunollo/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**A Universal Physics Engine for Cognitive Architectures**

Shunollo provides a pure, agnostic physics layer for translating any data stream into sensory qualia - enabling AI systems to "feel" their environment through entropy, roughness, viscosity, and other universal metrics.

> [!IMPORTANT]
> **Release baseline**: 0.3.14. See [release notes](docs/RELEASE_0.3.14.md) for behavior, migration requirements and limitations.
> Test counts and historical performance measurements do not establish production readiness or detection accuracy.
> The [host audit-log repair](docs/HOST_AUDIT_LOG.md) requires an explicit memory adapter and is included in 0.3.13.

## 100% Open Source

Shunollo is fully open source under the Apache 2.0 license. There is no "Enterprise Edition" or paid tier of the library itself. You get **everything**.

**Build whatever you want.** That's why we made this.

## Key Features

### Physics Engine (Multivariate Sensory Qualia)
Transform any data stream into a normalized physics fingerprint:
- **Mechanics**: Energy, Entropy, Roughness, Viscosity
- **Thermodynamics**: Temperature, Landauer Cost, Arrhenius Rates
- **Quantum**: Radical Pair coherence, Tunneling
- **Time Series**: Volatility, Lyapunov Exponents, Poisson Detection
- **High-Order**: Dissonance, Hamiltonian, Lagrangian Action

### Physics-RAG (Integrated v0.3.9) 🆕
**Retrieval-Augmented Generation for Sensation** - your AI remembers what it has "felt" before:

```python
from shunollo_core.memory.hippocampus import Hippocampus
from shunollo_core.models import ShunolloSignal

# Store an experience
hippo = Hippocampus()
signal = ShunolloSignal(energy=5.0, roughness=0.8, entropy=6.5)
hippo.remember(signal)

# Later: Déjà Vu - "Have I felt this before?"
query_vector = signal.to_vector(normalize=True)
similar_episodes = hippo.recall_similar(query_vector, k=3)

if similar_episodes:
    past_signal, distance = similar_episodes[0]
    print(f"Déjà Vu! This feels like {past_signal.timestamp} (distance: {distance})")
```

Nearest-neighbor retrieval returns stored examples for interpretation by the host. Recognition quality depends on the mapping, reference set and evaluation task.

## Architecture

```
shunollo/
├── shunollo_core/       # Pure Physics (Math only)
│   ├── physics/         # Mechanics, Thermo, Quantum, etc.
│   ├── brain/           # Autoencoder (Imagination)
│   ├── cognition/       # Active Inference + DDM
│   └── memory/          # Holographic + Hippocampus
└── shunollo_runtime/    # Nervous System (Event Bus)
```

```mermaid
graph LR
    subgraph Shunollo Core
    A[Physics Engine] --> B[18-dim Vector]
    B --> M[Hippocampus]
    M -->|Déjà Vu| B
    end
    
    subgraph Shunollo Runtime
    B --> C((Thalamus Bus))
    C --> D[Neural Cortex]
    C --> E[Reflex Agent]
    end
    
    D & E --> F[Decision]
```

> [!IMPORTANT]
> This repository contains later engine work that must be reconciled with the standalone Core extraction. Read [Core Reconciliation](docs/CORE_RECONCILIATION.md) before moving or consolidating components.

## Installation

```bash
pip install shunollo
```

## Quick start for 0.3.14

Round-trip a short count series through the versioned image mapping.

```python
from shunollo_core.perception.count_image import decode_counts, encode_counts

counts = [0, 2, 2, 5]
encoded = encode_counts(counts)
assert decode_counts(encoded, expected_bins=len(counts)) == counts
```

The encoder accepts 1–6,000 integer bins, each from 0 through 65,535. The calling application supplies the bin duration, coverage and source identity. A zero alone cannot distinguish silence from missing observations.

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Documentation

- [THE_SHUNOLLO_CODEX.md](THE_SHUNOLLO_CODEX.md) - Philosophy & Vision
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - **4 Real-World Examples** (Finance, Health, IoT, DevOps)
- [docs/whitepapers/](docs/whitepapers/) - Physics Theory
- [docs/technical/SENSORY_LEXICON.md](docs/technical/SENSORY_LEXICON.md) - Sensory Vocabulary
- [docs/technical/BRAIN_MAP.md](docs/technical/BRAIN_MAP.md) - Neural Architecture
- [docs/TESTING.md](docs/TESTING.md) - **Testing Strategy & Validation**

## Community

- 📖 [Roadmap](ROADMAP.md) - See what's coming
- 🐛 [Issue Tracker](https://github.com/TheLazyEyedJedi/Shunollo/issues) - Report bugs
- 💬 [Discussions](https://github.com/TheLazyEyedJedi/Shunollo/discussions) - Ask questions

## Contributing

We welcome research contributions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for architectural rules and setup instructions.

> **Note**: By contributing, you agree to our [Contributor License Agreement](.github/CLA.md).

### Scalar stream compatibility

See [Scalar stream contract and unreleased repair](docs/SCALAR_STREAM_CONTRACT.md) before using the historical generic transducer. It records the public signal contract, temporal measurements and release boundary.

See [pre-release review](docs/PRE_RELEASE_REVIEW.md) for neural safety repairs, compatibility changes, validation and remaining limits.
