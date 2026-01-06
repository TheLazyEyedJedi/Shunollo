
import os
import yaml
from pathlib import Path

# Defaults
DEFAULT_CONFIG = {
    "network": {
        "host": "127.0.0.1",
        "port": 8001,
        "backend_url": "http://127.0.0.1:8001",
        "monitor_interface": "auto"
    },
    "storage": {
        "db_path": "shunollo_core/data/shunollo.sqlite",
        "cache_dir": "shunollo_core/data/perception_cache",
        "codon_memory_path": "shunollo_core/data/codon_memory.json",
        "last_summary_path": "data/last_summary.json",
        "firewall_rules_path": "data/firewall_rules.yaml",
        "retention_seconds": 3600
    },
    "perception_matrix": {
        "enabled": True,
        "sample_rate": 0.05
    },
    "security": {
        "admin_user": os.getenv("SHUNOLLO_ADMIN_USER", "admin"),
        "admin_password": os.getenv("SHUNOLLO_ADMIN_PASSWORD", None) # Secure by default
    },
    "response": {
        "webhook_url": "",
        "script_dir": "scripts/responses",
        "allowed_scripts": ["echo_alert.py"]
    },
    "tts": {
        "enabled": True,
        "engine": "pyttsx3",
        "voice": "default",
        "rate": 150,
        "volume": 0.9
    }
}

# Mode-specific presets (Optional, can be requested in __init__)
MODE_PRESETS = {
    "TEST": {
        "storage": {"db_path": "shunollo_core/data/test_db.sqlite"},
        "network": {"monitor_interface": None},
        "perception_matrix": {"enabled": False}
    },
    "DEMO": {
        "network": {"monitor_interface": None}
    },
    "ENTERPRISE": {
        "perception_matrix": {"sample_rate": 1.0}
    }
}

class ConfigManager:
    def __init__(self, config_path: str = "shunollo.yaml", overrides: dict = None, mode: str = None):
        self._config = DEFAULT_CONFIG.copy()
        
        # 1. Load from YAML if exists
        self._load_from_file(config_path)
        
        # 2. Apply Mode Presets (explicit or environment-based if not specified)
        target_mode = mode or os.environ.get("SHUNOLLO_MODE", "DEFAULT").upper()
        if target_mode in MODE_PRESETS:
            self._merge(self._config, MODE_PRESETS[target_mode])
        
        # 3. Apply environment variable overrides
        # Check for SHUNOLLO_DB_URL (critical for Docker)
        db_url_env = os.environ.get("SHUNOLLO_DB_URL")
        if db_url_env:
            self._config["storage"]["db_url"] = db_url_env
        
        # 4. Apply explicit overrides (Highest Priority)
        if overrides:
            self._merge(self._config, overrides)

    def _load_from_file(self, config_path: str):
        p = Path(config_path)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge(self._config, user_config)
            except Exception:
                pass # Silent fail per library standards, or log to stderr

    def _merge(self, base, update):
        """Recursive dict merge"""
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    @property
    def network(self): return self._config["network"]
    
    @property
    def storage(self): return self._config["storage"]

    @property
    def perception_matrix(self): return self._config.get("perception_matrix", self._config.get("sensorium", {}))

    @property
    def sensorium(self): 
        # Deprecated: use perception_matrix
        return self.perception_matrix

    @property
    def security(self): return self._config.get("security", {})

    @property
    def llm(self): return self._config.get("llm", {})

    @property
    def response(self): return self._config.get("response", {})

# Singleton instance
config = ConfigManager()
