# Shunollo - The Biomimetic Physics Engine

[![PyPI version](https://img.shields.io/pypi/v/shunollo.svg)](https://pypi.org/project/shunollo/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/TheLazyEyedJedi/Shunollo/actions/workflows/ci.yml/badge.svg)](https://github.com/TheLazyEyedJedi/Shunollo/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**A Universal Physics Engine for Cognitive Architectures**

Shunollo provides a pure, agnostic physics layer for translating any data stream into sensory qualia - enabling AI systems to "feel" their environment through entropy, roughness, viscosity, and other universal metrics.

> [!IMPORTANT]
> **Status**: Production Ready
> *   **Physics**: Verified ($E=mv^{1.5}$)
> *   **Neuroscience**: Verified (Homeostatic Plasticity)
> *   **Ethics**: Verified (Safety Governor)
> *   **Security**: Hardened (No Pickle, Numpy only)

## 100% Open Source

Shunollo is fully open source under the Apache 2.0 license. There is no "Enterprise Edition" or paid tier of the library itself. You get **everything**.

**Build whatever you want.** That's why we made this.

## Architecture

```
shunollo/
├── shunollo_core/      # Pure Physics (Math only, zero dependencies)
└── shunollo_runtime/   # Nervous System (Redis, Agents, Thalamus)
```

```mermaid
graph LR
    subgraph Shunollo Core
    A[Physics Engine] --> B[Somatic Vector]
    end
    
    subgraph Shunollo Runtime
    B --> C((Thalamus Bus))
    C --> D[Neural Cortex]
    C --> E[Reflex Agent]
    end
    
    D & E --> F[Decision]
```

## Installation

```bash
pip install shunollo
```

## Quick Start

```python
from shunollo_core.physics import calculate_entropy, calculate_roughness
from shunollo_runtime import RedisThalamus, BaseAgent

# Pure physics calculation
entropy = calculate_entropy(data)
roughness = calculate_roughness(entropy, jitter=0.1)

# Distributed agent
class MyAgent(BaseAgent):
    def analyze(self, stimulus):
        return {"roughness": calculate_roughness(stimulus["entropy"])}
```

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Documentation

- [THE_SHUNOLLO_CODEX.md](THE_SHUNOLLO_CODEX.md) - Philosophy & Vision
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - **4 Real-World Examples** (Finance, Health, IoT, DevOps)
- [docs/whitepapers/](docs/whitepapers/) - Physics Theory
- [docs/technical/SENSORY_LEXICON.md](docs/technical/SENSORY_LEXICON.md) - Sensory Vocabulary

## Community

- 📖 [Roadmap](ROADMAP.md) - See what's coming
- 🐛 [Issue Tracker](https://github.com/shunollo/shunollo/issues) - Report bugs
- 💬 [Discussions](https://github.com/shunollo/shunollo/discussions) - Ask questions

## Contributing

We welcome research contributions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for architectural rules and setup instructions.

> **Note**: By contributing, you agree to our [Contributor License Agreement](.github/CLA.md).
