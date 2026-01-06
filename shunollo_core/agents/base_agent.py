# -----------------------------------------------------------------------------
# base_agent.py – The Neuron (Basic Signaling Unit)
# -----------------------------------------------------------------------------
"""
Technical role: Base class for all Agents.
Biological role: The Neuron / The Cell.
                 It has internal state (Memory), perceives stimuli (Packets), and fires signals (MirrorLink).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

import wave
import struct
import math
import os
from shunollo_core.perception.agent_perception import AgentPerception
from shunollo_core.perception.mirrorlink import MIRROR_LINK, Signal


class BaseAgent(AgentPerception, ABC):
    """Abstract base for all Shunollo agents (Hat, Manager, etc.)"""

    def __init__(self, name: str, role: str, color: str):
        self.name = name
        self.role = role
        self.color = color
        self.memory: List[Dict[str, Any]] = []
        
        # Synesthesia: Rhythm Memory (Core Platform Feature)
        self.beat_tracker = []
        
        super().__init__()

        # MirrorLink signal bus subscription
        MIRROR_LINK.subscribe(self.name, self._handle_signal)

    def analyze_rhythm(self, packet_timestamp: float, sound_volume: float) -> tuple[float, list[str]]:
        """
        Universal Rhythm Analysis (The Heartbeat).
        Returns (rhythm_score, rationale_bits).
        """
        rhythm_score = 0.0
        rationale_bits = []
        
        if sound_volume > 0.4:
            self.beat_tracker.append(packet_timestamp)
            
            # Prune old beats (> 30s window)
            self.beat_tracker = [t for t in self.beat_tracker if (packet_timestamp - float(t)) < 30.0]
            
            # Analyze intervals if we have at least 3 beats
            if len(self.beat_tracker) >= 3:
                 diffs = []
                 sorted_beats = sorted(self.beat_tracker)
                 for i in range(1, len(sorted_beats)):
                     diffs.append(sorted_beats[i] - sorted_beats[i-1])
                 
                 if diffs:
                     avg_diff = sum(diffs) / len(diffs)
                     variance = sum((d - avg_diff) ** 2 for d in diffs) / len(diffs)
                     
                     # Low variance = High Rhythm (Electronic/Automated Beacon)
                     # Variance < 0.1 means highly regular
                     if variance < 0.1 and avg_diff > 1.0:
                         rhythm_score = 0.9
                         rationale_bits.append(f"RHYTHM DETECTED: Interval {avg_diff:.2f}s (Var {variance:.4f})")
                         
        return rhythm_score, rationale_bits


    @abstractmethod
    def analyze(self, stimulus: Dict[str, Any], sensory: Optional[Dict[str, Any]], signal: Any = None):
        ...

    # ------------------------------------------------------------------ #
    # MirrorLink signaling
    # ------------------------------------------------------------------ #
    def send_signal(self, payload: Dict[str, Any]) -> None:
        """Broadcast a signal to all other agents."""
        MIRROR_LINK.emit(sender=self.name, payload=payload)

    def _handle_signal(self, signal: Signal) -> None:
        """Internal callback triggered by MirrorLink."""
        try:
            self.on_signal(signal)
        except Exception as e:
            print(f"[{self.name}] Error in on_signal: {e}")

    def on_signal(self, signal: Signal) -> None:
        """Override this method to handle received signals."""
        pass  # Default: do nothing

    # ------------------------------------------------------------------ #
    # Bionic Perception (The Sensorium)
    # ------------------------------------------------------------------ #
    def look_at_file(self, filepath: str) -> dict:
        """
        Physically reads the PPM image file and performs visual analysis.
        """
        try:
            if not os.path.exists(filepath):
                return {"score": 0.0, "error": "File not found"}

            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            data = []
            for line in lines:
                if line.startswith("#") or line.startswith("P3"): continue
                parts = line.split()
                data.extend([int(p) for p in parts if p.isdigit()])
            
            pixels = data[3:] if len(data) > 3 else []
            if not pixels:
                return {"score": 0.0, "error": "Empty image"}
                
            r_sum = sum(pixels[i] for i in range(0, len(pixels), 3))
            g_sum = sum(pixels[i] for i in range(1, len(pixels), 3))
            b_sum = sum(pixels[i] for i in range(2, len(pixels), 3))
            total_intensity = r_sum + g_sum + b_sum
            
            if total_intensity == 0:
                return {
                    "agent": self.name + "_Vision",
                    "score": 0.0,
                    "rationale": ["Blind: Total Darkness"],
                    "physical_observations": {"red_ratio": 0.0, "brightness_sum": 0}
                }
                
            red_ratio = r_sum / total_intensity
            score = round(min(red_ratio * 1.2, 1.0), 2)
            
            rationale = [f"Red Ratio: {red_ratio:.3f}"]
            if score > 0.7: rationale.append("High Red Intensity (Anomaly?)")
            elif score > 0.3: rationale.append("Moderate Activity")
            else: rationale.append("Visuals look calm")
                
            return {
                "agent": self.name + "_Vision",
                "score": score,
                "rationale": rationale,
                "physical_observations": {
                    "red_ratio": round(red_ratio, 3),
                    "brightness_sum": total_intensity
                }
            }
        except Exception as e:
            return {"agent": self.name + "_Vision", "error": str(e), "score": 0.0}

    def listen_to_file(self, filepath: str) -> dict:
        """
        Physically reads the WAV file and performs signal analysis.
        """
        try:
            if not os.path.exists(filepath):
                return {"score": 0.0, "error": "File not found"}

            with wave.open(filepath, 'rb') as wf:
                params = wf.getparams()
                num_frames = params.nframes
                raw_bytes = wf.readframes(num_frames)
                
                count = len(raw_bytes) // 2
                format_str = f"<{count}h"
                samples = struct.unpack(format_str, raw_bytes)
                
                sum_squares = sum(s**2 for s in samples)
                rms = math.sqrt(sum_squares / count)
                normalized_vol = rms / 32768.0
                
                zero_crossings = 0
                for i in range(1, len(samples)):
                    if (samples[i-1] > 0 and samples[i] < 0) or \
                       (samples[i-1] < 0 and samples[i] > 0):
                        zero_crossings += 1
                
                duration = max(num_frames / params.framerate, 0.001)
                estimated_hz = (zero_crossings / 2) / duration
                
                v_score = min(normalized_vol * 1.5, 0.5)
                f_score = min(estimated_hz / 5000.0, 0.5)
                
                final_score = round(v_score + f_score, 2)
                rationale = [f"RMS Vol: {normalized_vol:.3f}", f"Est Hz: {int(estimated_hz)}"]
                
                return {
                    "agent": self.name + "_Ear",
                    "score": final_score,
                    "rationale": rationale,
                    "physical_observations": {
                        "rms_amplitude": round(normalized_vol, 3),
                        "estimated_hz": int(estimated_hz)
                    }
                }
        except Exception as e:
            return {"agent": self.name + "_Ear", "error": str(e), "score": 0.0}
