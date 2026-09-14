# Core Reconciliation Note

## Why this exists

The main Shunollo repository predates the standalone `shunollo_core` extraction, but it also contains implementation work newer than that extraction. The repositories are not simply old and new copies.

- **Standalone `shunollo_core`** records the intended domain-agnostic separation.
- **This repository** contains richer later physics, memory, cognition, perception, ESN, Physics-RAG, and runtime work.
- **Omnisthesia** deployed with another bundled Core snapshot.

## Required interpretation

Do not copy this repository wholesale into standalone Core, and do not discard it in favor of the smaller extraction. Reconcile component by component.

Classify each subsystem as:

- **Migrate to Core** — generic and independently useful.
- **Keep in Shunollo runtime/reference tooling** — higher-level orchestration, examples, developer tooling, or release concerns.
- **Move to Omnisthesia** — network/security-specific.
- **Refactor** — reusable concept with domain coupling.
- **Archive** — duplicated, obsolete, or superseded.
- **Investigate** — behavior or intent is unclear.

## Architectural contract

1. Canonical Core must remain independently usable and domain-agnostic.
2. Core must not import Omnisthesia or encode network concepts.
3. Omnisthesia and future applications consume Core through stable public interfaces.
4. Generic functionality must be migrated with tests and behavioral comparison.
5. At least one unrelated, non-network example must prove the abstraction.
6. The vendored Core in Omnisthesia is removed only after dependency and deployment parity is verified.
7. Preserve history until unique features, tests, and release behavior are accounted for.

## Target state

```text
canonical shunollo_core
        |
        +-- Omnisthesia
        +-- Shunollo reference/runtime tooling
        +-- future domain applications
```

For the full history and non-regression rules, see `ARCHITECTURE_HISTORY.md` in the standalone `TheLazyEyedJedi/shunollo_core` repository.
