"""
Wernicke's Area
---------------
Biological Role: Language Comprehension & Production
Cybernatic Role: Translating 'Physics' (Feeling) into 'Narrative' (Description).

It does NOT use an LLM for everything (too slow).
It uses a deterministic "Reflexive Grammar" for immediate feedback, 
and can optionally delegate complex thoughts to an LLM.

Input: ShunolloSignal (roughness=0.8, harmony=0.2)
Output: "The environment is extremely harsh and dissonant. I detect aggressive friction."
"""

from typing import Dict, Any, Optional
from shunollo_core.models import ShunolloSignal

class WernickesArea:
    def __init__(self):
        self.vocabulary = {
            "roughness": {
                "high": ["grating", "harsh", "abrasive", "hostile", "aggressive"],
                "low": ["smooth", "fluid", "gentle", "calm"]
            },
            "harmony": {
                "high": ["harmonious", "resonant", "clear", "aligned"],
                "low": ["dissonant", "clashing", "jarring", "confused"]
            },
            "flux": {
                "high": ["chaotic", "turbulent", "frenetic", "wasteful"],
                "low": ["static", "stagnant", "frozen", "stable"]
            }
        }

    def narrate(self, signal: ShunolloSignal) -> str:
        """
        Converts a signal's physics into a coherent sentence.
        """
        # 1. Analyze dominant traits
        traits = []
        
        if signal.roughness > 0.7:
            traits.append(f"it feels {self._pick('roughness', 'high')}")
        elif signal.roughness < 0.2:
            traits.append(f"it feels {self._pick('roughness', 'low')}")
            
        if signal.harmony < 0.3:
            traits.append(f"the tone is {self._pick('harmony', 'low')}")
        
        if signal.flux > 0.8:
            traits.append(f"motion is {self._pick('flux', 'high')}")
            
        if not traits:
            return "I sense nothing remarkable."
            
        return "I sense that " + ", and ".join(traits) + "."

    def _pick(self, feature, level) -> str:
        # For now, deterministic first item. Later: random or context-aware.
        return self.vocabulary[feature][level][0]
