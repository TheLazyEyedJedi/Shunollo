"""
nervous_system.py
=================
The Central Event Bus for Sensory Perception.
Implements an Asynchronous Producer-Consumer pattern to dispatch sensory
signals to the various Cortexes without blocking the main application.

Architecture:
- Singleton `NervousSystem` instance.
- Thread-safe Queue for incoming events.
- Daemon Worker Thread for processing.
- Fault Isolation: Each Cortex call is wrapped in try/except.
"""
import threading
import queue
import time
from typing import Dict, Any
from shunollo_core.models import ShunolloSignal

# Cortex Imports (Lazy or direct - direct is fine for now)
# Cortex Imports (Lazy or direct - direct is fine for now)
from shunollo_core.perception.auditory_cortex import synthesize_audio_event, AuditoryCortex
from shunollo_core.perception.visual_cortex import synthesize_visual_event, analyze_scene
from shunollo_core.perception.haptic_driver import synthesize_haptic_event
from shunollo_core.perception.vocal_cords import synthesize_speech_event
from shunollo_core.cognition.wernickes_area import WernickesArea
from shunollo_core.cognition.brocas_area import BrocasArea
from shunollo_core.memory.hippocampus import Hippocampus
from shunollo_core.config import config

class NervousSystemEngine:
    def __init__(self):
        self._queue = queue.Queue()
        self._shutdown = False
        
        # New Biological Organs
        self.auditory = AuditoryCortex()
        self.wernicke = WernickesArea()
        self.broca = BrocasArea(enable_tts=False) # Config driven normally
        self.hippocampus = Hippocampus()
        
        # Start Worker
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="NervousSystemWorker")
        self._thread.start()
        print("[System] [NervousSystem] Online (Async Mode)")

    def dispatch(self, correlation_id: str, sensory_data: Dict[str, Any]):
        """
        Non-blocking dispatch of a sensory event.
        Returns immediately.
        """
        payload = {
            "id": correlation_id,
            "data": sensory_data
        }
        self._queue.put(payload)

    def publish_event(self, signal: ShunolloSignal, priority: int = 1):
        """
        Ingests a raw signal, runs it through the Brainstem (RAS),
        and if salient, dispatches it to the Cortex.
        """
        # 0. Brainstem Filtering (RAS)
        from shunollo_core.subcortex.ras import ras
        arousal, mechanism = ras.filter(signal)
        
        if not arousal:
            # Signal ignored by reticular formation
            # We don't log this to INFO to avoid spam, maybe DEBUG
            return

        # 1. Enqueue for Cortical Processing
        try:
            # Assuming self.event_queue should be self._queue based on existing code
            self._queue.put(signal, block=False) 
        except Exception:
            pass # Drop if brain is full (seizure prevention)

        except Exception:
            pass # Drop if brain is full (seizure prevention)

    def trigger_dream_cycle(self, duration_seconds: int = 5):
        """
        Initiates a 'REM Cycle'.
        Replays past memories into the Nervous System for re-analysis.
        """
        print("[System] [Sleep] Entering REM Cycle...")
        # Get approx batch based on duration (10 dreams / sec?)
        count = duration_seconds * 10
        dreams = self.hippocampus.dream(batch_size=count, random_sample=True)
        
        for dream in dreams:
            # Mark as dream to prevent re-recording
            dream.metadata["is_dream"] = True
            # WAKE IT UP (Bypass RAS? Or test RAS?)
            # We bypass RAS logic by injecting directly to queue, 
            # OR we rename publish_event.
            # publish_event runs RAS. We probably want RAS to filter dreams too (Nightmares vs boring dreams).
            self.publish_event(dream)
            
    def _worker_loop(self):
        while not self._shutdown:
            try:
                item = self._queue.get()
                # The original _process_event expects 'id' and 'data' from a dict.
                # If publish_event puts a ShunolloSignal directly, this needs adaptation.
                # For now, assuming item is still a dict or can be adapted.
                if isinstance(item, dict):
                    self._process_event(item["id"], item["data"])
                elif isinstance(item, ShunolloSignal):
                    # --- MEMORY CONSOLIDATION ---
                    # Only remember "Real" experiences, not dreams
                    is_dream = item.metadata.get("is_dream", False)
                    if not is_dream:
                        try:
                            self.hippocampus.remember(item)
                        except Exception:
                            pass # Don't crash on memory failure

                    # Adapt ShunolloSignal to legacy sensory format
                    import uuid
                    cid = item.metadata.get("correlation_id", str(uuid.uuid4()))
                    
                    # Adapt ShunolloSignal to legacy sensory format
                    import uuid
                    cid = item.metadata.get("correlation_id", str(uuid.uuid4()))
                    
                    # --- PERCEPTUAL PRE-PROCESSING ---
                    # 1. Isomorphic Translation (Physics -> Sensory)
                    # We need this EARLY to feed the Visual Cortex
                    sensory_payload = {
                        "light": {
                            "hue": item.hue,
                            "brightness": int(item.energy * 255),
                            "saturation": item.saturation
                        },
                        "position": {
                            "x": (item.spatial_x + 1.0) / 2.0, 
                            "y": (item.spatial_y + 1.0) / 2.0 
                        }
                    }
                    
                    # 2. visual Feedback Loop (Seeing)
                    visual_features = analyze_scene(sensory_payload)
                    item.metadata["visual_analysis"] = visual_features
                    
                    # --- COGNITIVE LOOP (Thinking) ---
                    # 3. Wernicke's Area (Narrative)
                    try:
                        narrative = self.wernicke.narrate(item)
                        # 4. Broca's Area (Expression)
                        urgency = item.energy * item.roughness
                        # If we see danger (Red), boost urgency
                        if visual_features.get("semantic_color") == "danger":
                            urgency = max(urgency, 0.8)
                            
                        self.broca.express(narrative, urgency=urgency)
                    except Exception as e:
                        print(f"[Warning] [Cognition] Error: {e}")

                    # --- LEGACY OUTPUT LOOP ---
                    # Check for pre-calculated auditory params
                    aud_meta = item.metadata.get("auditory", {})
                    
                    # Complete the sensory payload for legacy synthesizers
                    sensory_payload["sound"] = {
                        "pitch": aud_meta.get("pitch_base", item.frequency),
                        "timbre": aud_meta.get("timbre", "sine"),
                        "volume": item.energy,
                        "fm_mod": aud_meta.get("fm_mod", 0.0)
                    }
                    sensory_payload["raw_signal"] = item.dict()
                    sensory_payload.update(item.metadata)
                    
                    self._process_event(cid, sensory_payload)
                self._queue.task_done()
            except Exception as e:
                print(f"[Error] [NervousSystem] Worker Error: {e}")

    def _process_event(self, event_id: str, sensory_data: Dict[str, Any]):
        """
        Orchestrates the firing of all enabled cortexes.
        Fault Isolation: A crash in one does not stop the others.
        """
        # 1. Auditory Cortex
        try:
            if config.perception_matrix.get("enabled", True): # Check global switch
                synthesize_audio_event(event_id, sensory_data, correlation_id=event_id)
        except Exception as e:
            print(f"[Warning] [Auditory] Error: {e}")

        # 2. Visual Cortex
        try:
            synthesize_visual_event(sensory_data, correlation_id=event_id)
        except Exception as e:
            print(f"[Warning] [Visual] Error: {e}")

        # 3. Haptic Driver
        try:
            if "haptic" in sensory_data:
                synthesize_haptic_event(sensory_data, correlation_id=event_id)
        except Exception as e:
            print(f"[Warning] [Haptic] Error: {e}")

        # 4. Vocal Cords
        try:
            if "text" in sensory_data:
                # Check config specifically for TTS if needed, but module handles it
                synthesize_speech_event(sensory_data, correlation_id=event_id)
        except Exception as e:
            print(f"[Warning] [Vocal] Error: {e}")

# Singleton Instance
NervousSystem = NervousSystemEngine()
