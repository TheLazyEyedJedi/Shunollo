"""
ras.py - Reticular Activating System
====================================
The Brainstem's Gatekeeper.
Responsible for "Arousal" and "Attention".
Filters out "boring" stimuli to prevent Cortical Overload.

Biological Function:
- Regulates wakefulness and sleep-wake transitions.
- Filters out repetitive/background sensory input (habituation).
- Activates the cortex when "novel" or "high-energy" events occur.

Shunollo Implementation:
- Input: ShunolloSignal
- Logic:
    1. Check Energy (Volume). Low energy = Ignore?
    2. Check Flux (Change). Low flux (steady state) = Ignore?
    3. Check Novelty (via Hippocampus/Basal Ganglia). 
       Even low energy events might be important if they are NEW.
- Output: Boolean (Wake Up Cortex?)
"""
from typing import Tuple
from shunollo_core.models import ShunolloSignal

class ReticularActivatingSystem:
    
    def __init__(self):
        self.arousal_threshold = 0.2
        self.habituation_state = {} # simplistic local memory for now

    def filter(self, signal: ShunolloSignal) -> Tuple[bool, str]:
        """
        Decides if a signal is worthy of Cortical Attention.
        Returns: (passed_filter, mechanism)
        """
        # 0. Check Habituation (The Ignore Filter)
        if self._is_habituated(signal):
             return False, "habituation_suppression"

        # 1. Energy Gating (Volume)
        # Very quiet signals are usually noise (unless specific override)
        if signal.energy < 0.1:
            return False, "low_energy"

        # 2. Flux Gating (Change)
        # Steady-state hum (Flux ~ 0) is background noise.
        # We want to wake up on CHANGE.
        if signal.flux < 0.1:
            # Check for override (e.g. slow but persistent anomalies)
            # Roughness is the texture. Smooth + Low Flux = Boring.
            if signal.roughness < 0.2:
                return False, "steady_state_boredom"
                
        # 3. Novelty/Salience (The "Hey!" Factor)
        # High Roughness (Texture) always grabs attention (e.g. scratchy noise)
        if signal.roughness > 0.6:
            return True, "salience_texture"
            
        # High Dissonance (Conflict) always grabs attention
        if signal.dissonance > 0.5:
            return True, "salience_conflict"
            
        # Default: If it has decent energy and isn't boring, pass it.
        return True, "baseline_arousal"

    def _is_habituated(self, signal: ShunolloSignal) -> bool:
        """
        Biological Habituation:
        If a stimulus is repeated frequently without consequence, we stop noticing it.
        """
        import time
        now = time.time()
        
        # Create a "Sensation Fingerprint" (Coarse resolution)
        # We round to avoid jitter preventing habituation.
        fingerprint = (
            round(signal.energy, 1),
            round(signal.roughness, 1),
            round(signal.frequency, 1)
        )
        
        last_seen, count = self.habituation_state.get(fingerprint, (0, 0))
        
        # If seen recently (within 5 seconds)
        if now - last_seen < 5.0:
            count += 1
            self.habituation_state[fingerprint] = (now, count)
            
            # Threshold: After 3 repetitions, ignore it until it stops or changes
            if count > 3:
                # Exception: Never habituate to PAIN (High Dissonance/Roughness)
                if signal.dissonance > 0.8 or signal.roughness > 0.8:
                    return False
                return True
        else:
            # Reset if it's been a while
            self.habituation_state[fingerprint] = (now, 1)
            
        # Cleanup memory occasionally (dumb garbage collection)
        if len(self.habituation_state) > 1000:
            self.habituation_state.clear()
            
        return False

# Global Single Instance
ras = ReticularActivatingSystem()


