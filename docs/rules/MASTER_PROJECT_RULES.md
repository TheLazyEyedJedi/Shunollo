# Omnisthesia Master Project Rules

> **Goal**: Absolute Isomorphism between Human Neuroanatomy and AI Architecture.
> **Philosophy**: The Code *is* the Anatomy.

## 1. Architectural Integrity (The Schism)
*   **Brain vs Body**: `shunollo-core` (Brain) must NEVER import from `omnisthesia` (Body).
    *   **Core**: Pure math/physics, framework agnostic. It deals in abstract signals (e.g., `System Load`, `Entropy`). It DOES NOT know what "CPU" or "RAM" is.
    *   **App**: Workers, Routers, UI. This is where concrete mapping happens (e.g. `psutil.cpu_percent() -> System Load`).
*   **Data Decoupling**: The App must have its own data directory (`omnisthesia/data`). Never access `../shunollo_core/data` at runtime.
*   **Folder Hygiene**: `shunollo_core` (Underscore) is the active codebase. `shunollo-core` (Hyphen) is strictly for external packaging/shipping. Never import from the Hyphen folder.

## 2. Operational Standards (The Lessons)
*   **The Synaptic Seizure**: Use `SHUNOLLO_NO_SNIFFER=true` in cognitive containers to prevent feedback loops where the system sniffs its own traffic.
*   **The Synaptic Drain**: Test harnesses must poll the Thalamic bus (Redis) for queue completion (wait for 0), not just process exit, to avoid "Zero Results" race conditions.
*   **Stimulus ID Persistence**: Every physical vector must carry the original `stimulus_id` from Source to Judgment to ensure traceability.
*   **Environment Locking**: Use `os.getenv` for critical role-locking (flags are insufficient for subprocesses).
*   **Launcher**: ALWAYS use `.\launch_omnisthesia.ps1`.

## 3. Sensory Protocols (The Codex)
All new features must adhere to this isomorphic mapping.
*   **Rule**: `Shunollo Core` only sees the **Cybernetic Metric** (Agnostic).
*   **Rule**: `Omnisthesia` (App) is responsible for the **Interpretation** (Mapping concrete signals like CPU/RAM to the Metric).

| Biological | Cybernetic (Metric) | Interpretation (App Layer Source) |
|---|---|---|
| **Sight (Color)** | Protocol Identity | Port Number / Service Type |
| **Sight (Brightness)** | Magnitude | Packet Size / Volume / Saliency |
| **Roughness** | Entropy | Information Density / Encryption |
| **Temperature** | Volatility | Rate of Change / Flux |
| **Vibration** | Jitter | Inter-arrival Time Variance |
| **Muscle Stretch** | System Load | CPU/RAM Utilization (Concrete) |
| **Tension** | Queue Depth | Backpressure / Buffer Fill |
| **Kinesthesia** | Velocity | Throughput / Actions per Second |
| **Balance** | Stability | Route Flapping / TCP State Stability |
| **Acceleration** | Burstiness | Sudden Traffic Spikes |
| **Pain** | Error Rate | 5xx Errors / Dropped Packets |
| **Pungency** | Centrality | Graph Node Importance / Hops |
| **Scent Trail** | Threat Match | Known IOC / Threat Intel |
| **Taste (Sweet)** | Valid Syntax | Structured Data (JSON/XML) |
| **Taste (Bitter)** | Malicious | Shellcode / Exploits |
| **Taste (Sour)** | Corruption | Malformed / Broken Data |

## 4. UI Guidelines
*   **One True UI**: `omnisthesia/cortex/ui`. Ignore `_legacy_ui_quarantine`.
*   **Bridge**: Communication MUST go through `bridge.py` via WebSocket or `experiment_router.py`.

## 5. Deployment Checklist
1.  **Check Infrastructure**: Are Docker/Redis running?
2.  **Verify Backend**: Is port 8000 responsive?

## 6. Testing Protocol (Zero Drift)
*   **Order of Operations**:
    1.  **Data Gen**: `python -m scripts.scenarios.generate_clinical_data` (Must run first!)
    2.  **Unit**: `pytest tests/unit`
    3.  **Integration**: `pytest tests/integration`
    4.  **System**: `pytest tests/system`
*   **Rule**: Never skip Data Gen before Integration tests.

