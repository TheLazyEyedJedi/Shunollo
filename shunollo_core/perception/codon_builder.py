"""codon_builder.py
====================

Maps a single *percept unit* into symbolic **codon strings**.

A *percept* is expected to contain these top‑level keys::

    {
        "raw":   {...},   # original packet metadata
        "sound": {...},   # translated auditory vars (pitch, volume, etc.)
        "light": {...}    # translated visual vars (hue, brightness, etc.)
    }

The exporter returns exactly **three** codon strings – one per modality – in
a deterministic order *(sound, light, raw)*.  Down‑stream modules treat each
codon as an opaque symbolic token.

Example codon list::

    [
        "high_pitch_loud_buzzy",
        "warm_bright_rapid_pulse",
        "TCP_large_external"
    ]
"""  # noqa: E501

from typing import Dict, List, Tuple

# --------------------------------------------------------------------- #
#  Feature extractors
# --------------------------------------------------------------------- #
def _sound_features(sound: Dict) -> Tuple[str, str, str]:
    pitch = sound.get("pitch", 0)
    volume = sound.get("volume", 0)
    timbre = sound.get("timbre", "neutral")
    return (
        "high_pitch" if pitch > 180 else "low_pitch",
        "loud" if volume > 0.7 else "soft",
        timbre or "neutral",
    )

def _light_features(light: Dict) -> Tuple[str, str, str]:
    hue = light.get("hue", 0)
    brightness = light.get("brightness", 0)
    pulse = light.get("pulse_rate", 1)
    return (
        "warm" if hue < 180 else "cool",
        "bright" if brightness > 200 else "dim",
        "rapid_pulse" if pulse >= 3 else "slow_pulse",
    )

def _raw_features(raw: Dict) -> Tuple[str, str, str]:
    proto = raw.get("protocol", "UNK").upper()
    size = raw.get("size", 0)
    dst = raw.get("dst", "")
    return (
        proto,
        "large" if size > 1000 else "small",
        "internal" if str(dst).startswith("192.168") else "external",
    )

def _physics_features(physics: Dict) -> Tuple[str, str, str, str, str, str, str]:
    roughness = physics.get("roughness", 0.0)
    flux = physics.get("flux", 0.0)
    viscosity = physics.get("viscosity", 0.0)
    volatility = physics.get("volatility", 0.0)
    action = physics.get("action", 0.0)
    hamiltonian = physics.get("hamiltonian", 0.0)
    ewr = physics.get("ewr", 1.0)
    
    return (
        "ROUGH_TEXTURE" if roughness > 0.6 else "SMOOTH_FLOW",
        "HIGH_FLUX" if flux > 100.0 else "STABLE_BEAT",
        "VISCOUS_SLUDGE" if viscosity > 10.0 else "FLUID_DYNAMICS",
        "STOCHASTIC_DRIFT" if volatility > 0.5 else "GAUSSIAN_WALK",
        "LAGRANGIAN_STRAIN" if action > 0.7 else "LEAST_ACTION",
        "HAMILTONIAN_COMPLEX" if hamiltonian > 0.6 else "SYSTEMIC_EASE",
        "STEALTH_EWR" if ewr < 0.2 else "OPEN_PATH",
    )

# --------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------- #
def build_codons(percept: Dict[str, Dict]) -> List[str]:
    """Return 4 codon strings derived from *percept* (Sound, Light, Raw, Physics)."""
    raw = percept.get("raw", {})
    sound = percept.get("sound", {})
    light = percept.get("light", {})
    physics = percept.get("physics", {})

    return [
        "_".join(_sound_features(sound)),
        "_".join(_light_features(light)),
        "_".join(_raw_features(raw)),
        "_".join(_physics_features(physics)),
    ]
