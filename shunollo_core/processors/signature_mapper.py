"""
signature_mapper.py -- maps symbolic signatures to domain-level events
Includes:
- match_signature(event)
- label(event)
- map_alert_level(event)
- suggest_action(event)
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Load from local YAML rules
_SIGNATURE_FILE = Path(__file__).parent / "signature_rules.yaml"
try:
    with _SIGNATURE_FILE.open("r", encoding="utf-8") as f:
        RULES = yaml.safe_load(f)
except Exception as e:
    print(f"[signature_mapper] [X] Failed to load {str(_SIGNATURE_FILE)}: {e}")
    RULES = []

def match_signature(event: Dict[str, Any]) -> Dict[str, Any]:
    for rule in RULES:
        thresholds = rule.get("thresholds", {})
        passed = True

        if "sound_min" in thresholds and event.get("avg_sound_score", 0) < thresholds["sound_min"]:
            passed = False
        if "sound_max" in thresholds and event.get("avg_sound_score", 0) > thresholds["sound_max"]:
            passed = False
        if "light_min" in thresholds and event.get("avg_light_score", 0) < thresholds["light_min"]:
            passed = False
        if "light_max" in thresholds and event.get("avg_light_score", 0) > thresholds["light_max"]:
            passed = False
        if "conf_min" in thresholds and event.get("avg_confidence", 0) < thresholds["conf_min"]:
            passed = False
        if "conf_max" in thresholds and event.get("avg_confidence", 0) > thresholds["conf_max"]:
            passed = False
        if "severity_min" in thresholds and event.get("severity", 0) < thresholds["severity_min"]:
            passed = False
        if "severity_max" in thresholds and event.get("severity", 0) > thresholds["severity_max"]:
            passed = False

        if passed:
            return rule

    return {
        "id": "unknown",
        "description": "No matching rule found",
        "mitre": [],
        "escalate": False,
        "action": "none"
    }

def label(event: Dict[str, Any]) -> str:
    return match_signature(event).get("id", "unknown")

def map_alert_level(event: Dict[str, Any]) -> int:
    sig = match_signature(event)
    if sig.get("escalate") is True:
        return 3
    sev = event.get("severity", 0)
    if sev > 0.8:
        return 3
    elif sev > 0.5:
        return 2
    elif sev > 0.2:
        return 1
    return 0

def suggest_action(event: Dict[str, Any]) -> str:
    return match_signature(event).get("action", "log-only")
