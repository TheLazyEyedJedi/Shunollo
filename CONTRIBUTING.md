# Contributing to Shunollo

**"The Code is the Anatomy."**

Thank you for your interest in contributing to Shunollo. We are building the world's first Biomimetic Physics Engine for Cognitive Architectures. To maintain the integrity of the ["Isomorphic Architecture"](README.md#architecture), we ask all internal and external contributors to follow these guidelines.

## 1. The Prime Directive (The Schism)
Shunollo is strictly divided into two domains. You must know which one you are editing:

*   **`shunollo_core/` (The Brain)**: Pure Physics and Math.
    *   **Rule**: NO external dependencies (except `numpy`).
    *   **Rule**: NO networking code. NO database access.
    *   **Rule**: Must run offline.
*   **`shunollo_runtime/` (The Nerves)**: The transport layer.
    *   **Rule**: Moves data from A to B (e.g., Redis, HTTP).
    *   **Rule**: Never contains business logic.

## 2. Development Setup

### Prerequisite
*   Python 3.10+
*   Poetry (Recommended) or pip

### Installation
```bash
git clone https://github.com/shunollo-labs/shunollo.git
cd shunollo
pip install -e ".[dev]"
```

## 3. Security Standards (The Immune System)
We maintain a "Zero Risk" posture for the core library.

*   **Banned**: `pickle` (Use `json` or `numpy.savez`).
*   **Banned**: `eval()` / `exec()`.
*   **Banned**: Network calls in `shunollo_core`.
*   **Mandatory**: All input vectors must be validated/clamped before processing.

## 4. Running Tests
We require all tests to pass before merging.

### Run All Tests
```bash
pytest tests/ -v
```

## 5. Code Style (The Codex)
*   **Docstrings**: All public functions must explain the *Physics Mapping* (e.g., "Maps CPU Load to Lagrangian Action").
*   **Type Hinting**: Required for all new code.
*   **Zero-Shot**: If a new feature requires "Training", it belongs in the Learning module, not Physics.

## 6. Pull Requests
1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/my-new-sense`).
3.  Add tests.
4.  Submit PR.

## 7. Community & Conduct
We treat code like biology. Respect the organism.
*   Be kind to fellow researchers.
*   Debate the Physics, not the Person.

## 8. Contributor License Agreement (CLA)

By submitting a pull request, you agree to our [Contributor License Agreement](.github/CLA.md). This ensures all contributions are properly licensed under Apache 2.0.

For questions about the CLA, contact: **legal@shunollo.org**
