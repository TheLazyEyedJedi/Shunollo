"""
haptic_driver.py
================
The Physical Touch Driver.
Converts "Haptic" sensory variables into device-agnostic instruction files (JSON).

Protocol (Input Dict):
{
    "haptic": {
        "intensity": 0.0-1.0,   # Vibration Strength
        "pattern": "pulse",     # "pulse", "steady", "wave"
        "duration": 0.5         # Seconds
    }
}

Output:
Writes a JSON file to the 'cache_dir' that external drivers (e.g., bHaptics router) can pick up.
"""
import os
import json
import time
import uuid
from typing import Dict, Any
from shunollo_core.config import config

def synthesize_haptic_event(sensory_data: Dict[str, Any], output_dir: str = None, correlation_id: str = None, **kwargs) -> str:
    """Generates a JSON Haptic Instruction file."""
    if output_dir is None:
        output_dir = config.storage["cache_dir"]
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Extract Haptic Data
    haptic = sensory_data.get("haptic", {})
    
    # Defaults
    intensity = haptic.get("intensity", 0.0)
    pattern = haptic.get("pattern", "pulse")
    duration = haptic.get("duration", 0.1)
    
    # 2. Construct Instruction Payload
    # This schema is designed to be generic enough for:
    # - Game Controllers (Rumble)
    # - Haptic Vests (bHaptics)
    # - Wearables (Neosensory)
    instruction = {
        "event_id": correlation_id or str(uuid.uuid4()),
        "timestamp": time.time(),
        "type": "haptic_effect",
        "parameters": {
            "intensity": max(0.0, min(1.0, float(intensity))),
            "pattern": str(pattern),
            "duration_ms": int(duration * 1000)
        }
    }
    
    # 3. Write File
    # Naming convention: haptic_{timestamp}_{random}.json
    filename = f"haptic_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}.json"
    filepath = os.path.join(output_dir, filename)
    absolute_path = os.path.abspath(filepath)
    
    with open(absolute_path, "w") as f:
        json.dump(instruction, f, indent=2)

    # 4. Log to Artifact Database (if available)
    # 4. Log to Artifact Database (if available)
    if correlation_id and "memory" in kwargs and kwargs["memory"]:
        try:
            kwargs["memory"].store_artifact(correlation_id, "haptic", filename)
        except Exception:
            pass
            
    return absolute_path
