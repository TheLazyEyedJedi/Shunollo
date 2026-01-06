"""
vocal_cords.py
==============
The Core Speech Synthesis Engine.
Converts "Text" sensory variables into Audio artifacts (WAV).

Protocol (Input Dict):
{
    "text": {
        "content": "Intrusion detected.",
        "voice": "female", # optional hint
        "rate": 150        # WPM
    }
}

Architecture:
- Uses `pyttsx3` for offline TTS.
- WRAPS `runAndWait` in a separate process/thread because it blocks the main loop.
"""
import os
import time
import uuid
import threading
from typing import Dict, Any
from shunollo_core.config import config

# Import library safely (user might not have installed it yet)
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("[WARN] [VocalCords] pyttsx3 not found. Speech disabled.")

def _tts_worker(text: str, output_path: str, rate: int):
    """
    Worker function to run in a separate thread/process.
    Initializes a localized engine instance to avoid COM threading issues.
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        # Verify output directory exists (redundant but safe)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to file
        engine.save_to_file(text, output_path)
        engine.runAndWait() 
        # Note: runAndWait blocks until file is written
    except Exception as e:
        print(f"[X] [VocalCords] TTS Worker Error: {e}")

from shunollo_core.memory.base import AbstractMemory

def synthesize_speech_event(sensory_data: Dict[str, Any], output_dir: str = None, correlation_id: str = None, memory: AbstractMemory = None) -> str:
    """Generates a Speech WAV file from text."""
    if not HAS_TTS:
        return ""

    if output_dir is None:
        output_dir = config.storage["cache_dir"]
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Extract Text Data
    txt_data = sensory_data.get("text", {})
    content = txt_data.get("content", "")
    
    if not content:
        return ""
        
    rate = txt_data.get("rate", config._config.get("tts", {}).get("rate", 150))
    
    # 2. File Path
    filename = f"speech_{int(time.time())}_{uuid.uuid4().hex[:4]}.wav"
    filepath = os.path.join(output_dir, filename)
    absolute_path = os.path.abspath(filepath)
    
    # 3. Generate (Threaded)
    # We use a thread because engine.save_to_file + runAndWait can block for 1-2s
    # Note: On Windows, COM objects in threads can be tricky. 
    # For a robust production system, we might use a dedicated Process or Queue.
    # For MVP, we spawn a thread that initializes its OWN engine.
    t = threading.Thread(target=_tts_worker, args=(content, absolute_path, rate))
    t.start()
    
    # We return the path immediately (it will exist in ~500ms)
    
    # 4. Log artifact
    if correlation_id and memory:
        memory.store_artifact(correlation_id, "speech", filename)
            
    return absolute_path
