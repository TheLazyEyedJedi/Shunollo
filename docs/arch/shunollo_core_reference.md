# Shunollo Core: Technical Module Reference

## Overview
`shunollo_core/` is the **Domain-Agnostic Brain SDK**. It contains zero network-specific logic and can theoretically process any time-series data stream (logs, metrics, audio, etc.).

## Directory Structure & Purpose

### 📊 `physics.py` - The Mathematical Foundation
**Purpose**: Converts raw entropy into physical vectors using Lagrangian/Hamiltonian mechanics.

**Key Functions**:
- `calculate_roughness()`: Shannon Entropy + Compression Ratio
- `calculate_flux()`: Inter-arrival time variance (Jitter)
- `calculate_viscosity()`: Latency drag coefficient
- `calculate_action()`: Lagrangian principle (T - V)

**Agnosticism**: Takes generic byte arrays, not packets.

---

### 🧠 `perception/` - Sensory Transduction
**Purpose**: Converts physical vectors into perceptual qualia.

| Module | Biological Analog | Function |
|--------|-------------------|----------|
| `auditory_cortex.py` | Primary Auditory Cortex (A1) | Converts entropy → pitch, flux → timbre |
| `visual_cortex.py` | Primary Visual Cortex (V1) | Renders state as color/motion for UI |
| `meta_gene_layer.py` | Synaptic Plasticity | Hebbian learning for pattern reinforcement |
| `physics_worker.py` | **Level 1 Transduction** | Redis consumer for raw→physics conversion |

---

### 🤖 `agents/` - The Base Intelligence
**Purpose**: Universal agent interface and base heuristics.

| Module | Role |
|--------|------|
| `base_agent.py` | Abstract interface all agents inherit from |
| `base_hat_agent.py` | Physics-aware agent with rhythm tracking |

**Critical**: All agents in `omnisthesia/agents/` extend `BaseHatAgent`.

---

### 💾 `storage/` - The Hippocampus
**Purpose**: Long-term memory persistence.

| Module | Function |
|--------|----------|
| `database.py` | SQLAlchemy ORM for events, telemetry, artifacts |
| `db_models.py` | Schema definitions (History, Telemetry, Codons) |

---

### 🔄 `feedback/` - Codon Memory System
**Purpose**: Reinforcement learning and pattern consolidation.

**Key Components**:
- `codon_memory.py`: Stores successful detection patterns
- `reinforcement.py`: Wilson Score confidence intervals
- `meta_encoding.py`: Dynamic weight adjustment

---

### ⚙️ `processors/` - Background Workers
**Purpose**: Asynchronous analysis pipelines.

| Module | Function |
|--------|----------|
| `signature_library.py` | Known-pattern matching (Basal Ganglia) |
| `perceptual_clusterer.py` | Groups similar signals into episodes |

---

### 🔌 `transport/` - The Thalamus
**Purpose**: Redis-based synaptic relay (Architecture 2.0).

**Critical Queues**:
- `shunollo:sensation_raw`: Unprocessed input
- `shunollo:sensation_physics`: Level 1 output
- `shunollo:cortex_broadcast`: Level 2 alerts

---

### 🎯 `actions/` & `motor/` - Effector Systems
**Purpose**: Execute defensive actions based on decisions.

| Module | Biological Analog | Function |
|--------|-------------------|----------|
| `defense_manager.py` | Amygdala (Fear Response) | Immediate threat blocking |
| `motor_cortex.py` | Primary Motor Cortex | System call execution |

---

## Design Philosophy

### The Agnosticism Principle
> **Rule**: `shunollo_core` must NEVER import from `omnisthesia`.

This ensures the Brain SDK can be reused for:
- Application security (current)
- Infrastructure monitoring (future)
- Financial fraud detection (future)

### The Isomorphic Contract
Every class maps to a biological structure. If you can't name the biological analog, the class shouldn't exist.
