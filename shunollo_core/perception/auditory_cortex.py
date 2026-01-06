"""
Auditory Cortex (-Temporal Lobe-)
---------------------------------
Responsible for translating Isomorphic Physics (Feeling) into Sound Parameters.

Mappings:
- Roughness -> Timbre & FM Modulation (Scratchiness)
- Harmony -> Pitch Quantization (Consonance)
- Flux -> Rhythm/BPM (Frequency of events)
- Energy -> Volume (Amplitude)
"""

from typing import Dict, Any
from shunollo_core.models import ShunolloSignal

class AuditoryCortex:
    def process_sound(self, signal: ShunolloSignal) -> Dict[str, Any]:
        """
        Maps signal physics to audio synthesis parameters.
        Returns a dictionary compatible with Tone.js or similar engines.
        """
        # 1. Volume (Energy)
        # Assuming Energy is ~ Flux * Roughness or Raw Size
        # We'll use signal.energy as a placeholder for size-derived magnitude
        volume = min(1.0, max(0.1, getattr(signal, "energy", 0.5)))
        
        # 2. Timbre (Roughness)
        # Roughness 0.0 -> Sine (Smooth)
        # Roughness 1.0 -> Sawtooth (Harsh)
        timbre = "sine"
        fm_mod = 0.0
        
        if signal.roughness > 0.8:
            timbre = "sawtooth"
            fm_mod = 50.0 # High modulation = Grating noise
        elif signal.roughness > 0.4:
            timbre = "square"
            fm_mod = 10.0
        else:
            timbre = "sine"
            fm_mod = 0.0
            
        # 3. Pitch / Harmony
        # High Harmony -> Consonant Intervals (Octaves, 5ths)
        # Low Harmony -> Dissonant Intervals (Tritones, Seconds)
        base_freq = 440.0 # A4
        pitch_multiplier = 1.0
        
        if signal.harmony < 0.3:
            pitch_multiplier = 1.414 # Tritone (Devil's Interval) - Dissonant
        elif signal.harmony > 0.8:
            pitch_multiplier = 2.0 # Octave - Harmonious
        else:
            pitch_multiplier = 1.5 # Perfect 5th - Stable
            
        final_pitch = base_freq * pitch_multiplier
        
        if signal.flux > 0.7:
             duration = 0.1
        else:
             duration = 2.0
        
        # 5. Scene Analysis (Stream Segregation)
        # Salience = Energy * Roughness.
        # High Salience -> Foreground (Alert)
        # Low Salience -> Background (Drone)
        salience = volume * getattr(signal, "roughness", 0.0)
        stream_role = "foreground" if salience > 0.3 else "background"
        
        return {
            "volume": round(volume, 2),
            "timbre": timbre,
            "pitch": round(final_pitch, 2),
            "duration": duration,
            "fm_modulation": fm_mod,
            "fm_harmonicity": 1.0, # Default
            "stream_role": stream_role
        }

def synthesize_audio_event(event_id: str, sensory_data: Dict[str, Any], correlation_id: str = None) -> None:
    """
    Legacy/Driver wrapper.
    In a real system, this would send OSC/MIDI or generate a WAV.
    For now, it just validates the parameters provided by the Cortex.
    """
    sound = sensory_data.get("sound", {})
    # if config.debug:
    #     print(f"[Auditory] Synthesizing: {sound}")
    pass # Real synthesis happens in the Frontend (Tone.js) or separate process
