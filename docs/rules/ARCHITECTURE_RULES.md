# Architecture Rules (The Schism)

These rules MUST be followed to maintain the integrity of the Isomorphic Architecture.

## 1. The Prime Directive: Core vs Applications
*   **Shunollo Core** (`shunollo_core/`) is the **Brain** (Library).
    *   It contains agnostic physics, signal processing, and memory.
    *   **RULE**: It must NEVER import from external applications. It must be deployable standalone.
    *   **RULE**: Code here must be pure Python/math, minimizing external dependencies.
*   **Applications** (e.g., Omnisthesia) are the **Body** (Application).
    *   They contain the IO (Sensors), UI (Cortex), and API (Routers).
    *   **RULE**: They treat `shunollo_core` as a 3rd-party library.
    *   **RULE**: All "Business Logic" lives in applications, not in the core.

## 2. The Thalamic Bridge
*   **RULE**: The UI must NEVER speak directly to the Physics Engine.
*   **Mechanism**: All communication MUST pass through the runtime bridge or API.
*   **Data Flow**: `Workers -> Thalamus -> Bridge -> UI`.

## 3. Headless Mode
*   **RULE**: The core must support "Headless Mode" (No UI) for CLI/server execution.
