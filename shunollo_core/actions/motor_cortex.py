"""
MotorCortex - The Hand of the Agent
===================================
Technical Role: Abstract Output Interface
Biological Role: Motor Cortex (Voluntary Movement)

The Brain (Shunollo Core) does not know "how" to move the hand (iptables, AWS WAF, etc).
It only knows "that" it wants to move the hand.

This module provides the singleton `MotorCortex` which receives `signals` from the Prefrontal Cortex
(Manager/DefenseManager) and dispatches them to registered `MotorDrivers`.
"""

from typing import Dict, Any, List, Optional, Protocol

class MotorDriver(Protocol):
    """
    Protocol that any body-part (Action Driver) must implement.
    """
    name: str
    
    def execute(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

class MotorCortex:
    _instance = None
    _drivers: Dict[str, MotorDriver] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MotorCortex, cls).__new__(cls)
            cls._instance._drivers = {}
        return cls._instance

    @classmethod
    def register_driver(cls, driver: MotorDriver):
        """
        The Body (App) calls this to attach a muscle to the bone.
        """
        print(f"[MotorCortex] Connecting nerve to muscle: {driver.name}")
        cls._drivers[driver.name] = driver

    @classmethod
    def signal(cls, action_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        The Mind calls this to command an action.
        It fires all relevant drivers for that action type.
        """
        results = []
        # Broadcast signal to all muscles (simple version)
        # In future, we could route specific actions to specific drivers.
        for name, driver in cls._drivers.items():
            try:
                # We assume all drivers handle the signal or ignore it gracefully
                # Or we can check if they support it.
                # For Phase 27, we broadcast.
                res = driver.execute(action_type, payload)
                if res:
                    res["driver"] = name
                    results.append(res)
            except Exception as e:
                print(f"[MotorCortex] Muscle Spasm in {name}: {e}")
                results.append({"driver": name, "error": str(e), "status": "failed"})
        
        return results

# Global singleton access
motor_cortex = MotorCortex()
