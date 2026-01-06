"""
shunollo_core/api.py - The Library Face
--------------------------------------
Formal entry point for host applications to interact with the Shunollo Perception Engine.
"""
from typing import Optional, Dict
from shunollo_core.config import ConfigManager, config as global_config
from shunollo_core.perception.perception_bus import subscribe as subscribe_sensory
from shunollo_core.perception.mirrorlink import MIRROR_LINK

def initialize(config_path: str = "shunollo.yaml", overrides: Optional[Dict] = None, mode: Optional[str] = None):
    """
    Initialize the Shunollo Engine with custom settings.
    
    :param config_path: Path to the YAML configuration file.
    :param overrides: Dictionary of explicit configuration overrides.
    :param mode: Optional 'TEST', 'DEMO', or 'ENTERPRISE' preset.
    """
    # 1. Update Global Config
    new_config = ConfigManager(config_path=config_path, overrides=overrides, mode=mode)
    global_config._merge(global_config._config, new_config._config)
    
    print(f"[Shunollo] Engine Initialized (Mode: {mode or 'DEFAULT'})")

class Engine:
    """High-level handle to the Perception Engine."""
    
    @staticmethod
    def shutdown():
        """Gracefully shutdown engine resources."""
        MIRROR_LINK.clear()
        
    @staticmethod
    def on_sensation(callback):
        """Subscribe to raw sensory frames (Light/Sound)."""
        subscribe_sensory(callback)
        
    @staticmethod
    def on_signal(signal_name, callback):
        """Subscribe to high-level agent signals."""
        MIRROR_LINK.subscribe(signal_name, callback)
