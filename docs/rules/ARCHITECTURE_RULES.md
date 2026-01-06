# Architecture Rules (The Schism)

These rules MUST be followed to maintain the integrity of the Isomorphic Architecture.

## 1. The Prime Directive: Brain vs Body
*   **Shunollo Core** (`shunollo-core/`) is the **Brain** (Library).
    *   It contains agnostic physics, signal processing, and memory.
    *   **RULE**: It must NEVER import from `omnisthesia`. It must be deployable standalone.
    *   **RULE**: Code here must be pure Python/math, minimizing external dependencies.
*   **Omnisthesia** (`omnisthesia/`) is the **Body** (Application).
    *   It contains the IO (Sensors/Network), UI (Cortex), and API (Routers).
    *   **RULE**: It treats `shunollo-core` as a 3rd-party library.
    *   **RULE**: All "Business Logic" (e.g., Clinical Trials) lives here.

## 2. The Thalamic Bridge
*   **RULE**: The UI (`cortex/ui`) must NEVER speak directly to the Physics Engine.
*   **Mechanism**: All communication MUST pass through the `bridge.py` WebSocket or the `experiment_router.py` API.
*   **Data Flow**: `Workers -> Redis (Thalamus) -> Bridge -> UI`.

## 3. Deployment
*   **RULE**: Always launch via `.\launch_omnisthesia.ps1`.
*   **RULE**: The system must support "Headless Mode" (No UI) for Docker execution.
