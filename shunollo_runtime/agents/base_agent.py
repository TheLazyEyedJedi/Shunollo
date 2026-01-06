"""
BaseAgent - The Neuron (Basic Signaling Unit) for the Runtime
--------------------------------------------------------------
Technical role: Base class for all Agents in the Shunollo Runtime.
Biological role: The Neuron / The Cell.
                 It has internal state (Memory), perceives stimuli, and fires signals via Thalamus.

This agent connects to the Synaptic Bus (Thalamus) for communication.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time

from ..interfaces import AbstractThalamus


class BaseAgent(ABC):
    """
    Abstract base for all Shunollo Runtime agents.
    Connects to the Thalamus (Synaptic Bus) for distributed communication.
    """

    def __init__(
        self,
        name: str,
        role: str,
        thalamus: Optional[AbstractThalamus] = None,
        input_channel: str = "stimuli",
        output_channel: str = "qualia",
    ):
        self.name = name
        self.role = role
        self.thalamus = thalamus
        self.input_channel = input_channel
        self.output_channel = output_channel
        
        # Internal state
        self.memory: List[Dict[str, Any]] = []
        self._running = False
        
        # Synesthesia: Rhythm Memory (Core Platform Feature)
        self.beat_tracker: List[float] = []

    # ------------------------------------------------------------------ #
    # Core Analysis (Override in subclasses)
    # ------------------------------------------------------------------ #
    @abstractmethod
    def analyze(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single stimulus and return the result (Qualia).
        Must be implemented by subclasses.
        """
        pass

    # ------------------------------------------------------------------ #
    # Rhythm Analysis (Universal Heartbeat)
    # ------------------------------------------------------------------ #
    def analyze_rhythm(self, packet_timestamp: float, sound_volume: float) -> tuple[float, list[str]]:
        """
        Universal Rhythm Analysis (The Heartbeat).
        Returns (rhythm_score, rationale_bits).
        """
        rhythm_score = 0.0
        rationale_bits = []
        
        if sound_volume > 0.4:
            self.beat_tracker.append(packet_timestamp)
            
            # Prune old beats (>30s window)
            self.beat_tracker = [t for t in self.beat_tracker if (packet_timestamp - float(t)) < 30.0]
            
            # Analyze intervals if we have at least 3 beats
            if len(self.beat_tracker) >= 3:
                sorted_beats = sorted(self.beat_tracker)
                diffs = [sorted_beats[i] - sorted_beats[i-1] for i in range(1, len(sorted_beats))]
                
                if diffs:
                    avg_diff = sum(diffs) / len(diffs)
                    variance = sum((d - avg_diff) ** 2 for d in diffs) / len(diffs)
                    
                    # Low variance = High Rhythm (Electronic/Automated Beacon)
                    if variance < 0.1 and avg_diff > 1.0:
                        rhythm_score = 0.9
                        rationale_bits.append(f"RHYTHM DETECTED: Interval {avg_diff:.2f}s (Var {variance:.4f})")
                        
        return rhythm_score, rationale_bits

    # ------------------------------------------------------------------ #
    # Thalamus I/O (Distributed Communication)
    # ------------------------------------------------------------------ #
    def publish_result(self, result: Dict[str, Any]) -> bool:
        """Publish a result (Qualia) to the output channel."""
        if not self.thalamus:
            return False
        result["_agent"] = self.name
        result["_timestamp"] = time.time()
        return self.thalamus.publish_stimulus(self.output_channel, result)

    def consume_stimulus(self, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """Consume a stimulus from the input channel."""
        if not self.thalamus:
            return None
        return self.thalamus.consume_stimulus(self.input_channel, timeout=timeout)

    # ------------------------------------------------------------------ #
    # The Main Loop (The Heartbeat)
    # ------------------------------------------------------------------ #
    def run(self, max_iterations: Optional[int] = None) -> None:
        """
        The main agent loop. Consumes stimuli, processes them, and publishes results.
        
        Args:
            max_iterations: If set, run for this many iterations then stop.
                            If None, run indefinitely until stop() is called.
        """
        self._running = True
        iteration = 0
        
        print(f"[{self.name}] Agent starting on channels: {self.input_channel} -> {self.output_channel}")
        
        while self._running:
            if max_iterations is not None and iteration >= max_iterations:
                break
                
            stimulus = self.consume_stimulus(timeout=1)
            if stimulus:
                try:
                    result = self.analyze(stimulus)
                    self.publish_result(result)
                except Exception as e:
                    print(f"[{self.name}] Error processing stimulus: {e}")
            
            iteration += 1
        
        print(f"[{self.name}] Agent stopped after {iteration} iterations.")

    def stop(self) -> None:
        """Signal the agent to stop its run loop."""
        self._running = False

    # ------------------------------------------------------------------ #
    # Lifecycle Hooks
    # ------------------------------------------------------------------ #
    def on_start(self) -> None:
        """Called when the agent starts. Override for custom setup."""
        pass

    def on_stop(self) -> None:
        """Called when the agent stops. Override for custom teardown."""
        pass
