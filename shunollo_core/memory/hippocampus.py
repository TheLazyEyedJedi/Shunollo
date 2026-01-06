"""
Hippocampus (Episodic Memory)
-----------------------------
Biological Role: Consolidation of Short-term to Long-term memory. Spatial navigation.
Cybernatic Role: Stores raw Sensory Events (Episodes) for offline replay ('Dreaming').

Features:
- Append-only Log (JSONL) of ShunolloSignals.
- 'Dreaming' interface to recall past events.
"""
import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Generator
from shunollo_core.models import ShunolloSignal
from shunollo_core.config import config

class Hippocampus:
    def __init__(self):
        self.storage_path = Path(config.storage["cache_dir"]) / "episodic_memory.jsonl"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def remember(self, signal: ShunolloSignal) -> None:
        """
        Encodes a conscious experience (Signal) into Long-Term Memory.
        """
        # Serialize
        record = signal.dict()
        # Ensure timestamp is string
        if isinstance(record.get("timestamp"), datetime):
            record["timestamp"] = record["timestamp"].isoformat()
            
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def dream(self, batch_size: int = 10, random_sample: bool = True) -> Generator[ShunolloSignal, None, None]:
        """
        Recalls past experiences.
        If random_sample=True, picks random moments (Remixing).
        If False, picks most recent (Reflection).
        """
        if not self.storage_path.exists():
            return

        lines = self.storage_path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return

        if random_sample:
            selection = random.sample(lines, min(len(lines), batch_size))
        else:
            selection = lines[-batch_size:]

        for line in selection:
            try:
                data = json.loads(line)
                # Reconstruct Signal
                # Note: This might lose perfect fidelity if schema changes, 
                # but that's consistent with biological memory decay/distortion.
                yield ShunolloSignal(**data)
            except Exception as e:
                # Corrupted memory
                continue

    def clear_memory(self):
        """Amnesia."""
        if self.storage_path.exists():
            self.storage_path.unlink()
