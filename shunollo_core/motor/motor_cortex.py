"""
Motor Cortex (Primary)
----------------------
Biological Role: Voluntary Movement
Cybernetic Role: The 'Action Driver' registry.
Translates High-Level Intent (Manager decisions) into Low-Level System Calls.

Drivers:
1. FirewallDriver (Iptables/Nfqueue)
2. ScriptDriver (Python/Bash)
3. ExternalDriver (Reflex Injection)
"""
from typing import Dict, Any, Callable, List
import logging

class MotorCortex:
    def __init__(self):
        self.logger = logging.getLogger("MotorCortex")
        self.registry: Dict[str, Callable] = {}
        self.history: List[str] = []

    def register_reflex(self, nerve_name: str, action: Callable):
        """
        Connects a 'Nerve' (Action Name) to a Muscle (Function).
        e.g. register_reflex("block_ip", my_firewall_func)
        """
        self.registry[nerve_name] = action
        self.logger.info(f"Nerve connected: {nerve_name}")

    def execute_intent(self, nerve_name: str, **kwargs) -> bool:
        """
        Fires the nerve.
        """
        if nerve_name not in self.registry:
            self.logger.error(f"Motor Signal Failed: Nerve '{nerve_name}' severed or missing.")
            return False

        try:
            self.logger.info(f"Motor Cortex Firing: {nerve_name}")
            muscle = self.registry[nerve_name]
            muscle(**kwargs)
            self.history.append(f"{nerve_name}:SUCCESS")
            return True
        except Exception as e:
            self.logger.error(f"Motor Spasm (Error) in {nerve_name}: {str(e)}")
            self.history.append(f"{nerve_name}:FAILED")
            return False
            self.history.append(f"{nerve_name}:FAILED")
            return False

# Global Singleton (The Motor Homunculus)
motor_cortex = MotorCortex()
