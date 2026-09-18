# Shunollo 0.3.11

Release candidate. This patch restores symbolic trait reconstruction using explicit host-supplied count snapshots and independent `TraitMemory` instances. It removes the missing legacy-memory import, validates reconstruction atomically, and preserves the existing module-level API for in-memory use. Hosts own persistence and the selection of historical counts; learned weights are not counts.

The distribution includes the already-merged runtime audit middleware and its separate `shunollo_runtime` namespace. The release does not claim calibrated security accuracy, improved detection speed, or production readiness.

Validation before tagging: full tests across Python 3.10–3.12; clean installed-wheel signal, runtime-audit and trait checks; consuming application's actual wheel, browser, persistence and migration tests. See `docs/TRAIT_RECONSTRUCTION.md` for host integration requirements.

---

## Historical release notes (claims retained as historical, not revalidated here)

# Shunollo v0.3.9 Release Notes
v0.3.7: "Stable Release"

**Date**: 2026-01-09
**Status**: Production Stable (228 Tests Passing)

---

## 🚀 Major Milestone: Systematic Verification
**v0.3.9** marks the graduation of Shunollo to a stable, production-ready platform. This release completes the "Architecture 3.0" roadmap, featuring a fully modular physics core, verified sub-millisecond performance, and a comprehensive privacy hygiene scrub.

### 1. Performance Benchmarks (The Speed)
*   **Physics Latency**: ~21.5µs per calculation.
*   **Inference Latency**: ~0.07ms per cognitive cycle.
*   **Memory Retrieval**: ~48µs (Holographic Associative Memory).
*   **Result**: System is fully capable of sub-millisecond real-time cognitive loops.

### 2. End-to-End Functional Pipeline (The Flow)
*   **E2E Validation**: `tests/test_e2e_pipeline.py` verifies the full loop from **Signal Transduction** $\to$ **Nervous System Dispatch** $\to$ **Active Inference** $\to$ **Motor Action**.
*   **Vectorization**: Physics functions (Entropy, Roughness) now support high-performance NumPy vectorization.

### 3. Privacy & Sanitization (The Lock)
*   **Sanitized Codebase**: Scrubbed all internal project metadata, expert comments, and development phases.
*   **Hardened Privacy**: Updated `.gitignore` to prevent any future tracking of private audits, gap analyses, or agent-specific metadata.
*   **GitHub Integrity**: Successfully sanitized the public repository of runtime artifacts and accidental sensitive leaks.

---

## 🛠 Features & Fixes
*   **Decision Dynamics**: `DriftDiffusionModel` with urgency and refractory periods for biological realism.
*   **Thermodynamics**: Gradient-dependent cooling and Landauer heat tracking.
*   **API Consistency**: Standardized `UniversalAdapter` initialization and signal processing.

## 🧪 Verification
*   **Tiered Tests**: 156 Unit, 42 Integration, 26 Functional, 4 Performance.
*   **Result**: 100% Passing (228/228).

---

## 📦 Deploy / Release
- Official Tag: `v0.3.7`
- Branch: `main`
