"""
Broca's Area
------------
Biological Role: Speech Production
Cybernatic Role: The 'Expressive Output' engine.
It takes a 'Narrative' (from Wernicke's) or 'Command' (from Motor) and articulates it to the outside world.

Outputs:
1. Console (STDERR/STDOUT) - "Inner Monologue"
2. Dashboard (WebSocket) - "User Alert"
3. TTS (Text-to-Speech) - "Vocal Output"
"""
import logging
from typing import Optional

class BrocasArea:
    def __init__(self, enable_tts: bool = False):
        self.logger = logging.getLogger("BrocasArea")
        self.enable_tts = enable_tts
        self.history = []

    def express(self, wernickes_narrative: str, urgency: float = 0.0) -> None:
        """
        Articulates a thought.
        Urgency (0.0 - 1.0) determines the volume/channel.
        """
        
        # 1. Internal Monologue (Always)
        if urgency < 0.3:
            # Subconscious thought
            self.logger.debug(f"Thought: {wernickes_narrative}")
        elif urgency < 0.7:
             # Conscious speech
            self.logger.info(f"Said: {wernickes_narrative}")
            print(f">>> BRAIN: {wernickes_narrative}")
        else:
            # Shouting / Alert
            self.logger.warning(f"SHOUTED: {wernickes_narrative}")
            print(f"!!! BRAIN: {wernickes_narrative.upper()} !!!")

        # 2. TTS (Optional)
        if self.enable_tts and urgency > 0.5:
            self._synthesize_voice(wernickes_narrative)
            
        self.history.append(wernickes_narrative)

    def _synthesize_voice(self, text: str):
        # Placeholder for pyttsx3 or similar
        pass
