"""
glossary.py – Shunollo Symbolic Glossary
Cross-domain terms from cybersecurity, sound engineering, color theory, and genetics.
This file defines core symbolic vocabulary used in codons, signatures, scoring, and agent feedback.
"""

GLOSSARY = {
    "cybersecurity": {
        "TTP": "Tactics, Techniques, and Procedures – patterns of behavior used by threat actors.",
        "MITRE ATT&CK": "A structured matrix of known adversary behaviors and exploits.",
        "Escalation": "A rising severity of attack or system compromise.",
        "Reconnaissance": "Early-stage probing or scanning activity."
    },
    "sound": {
        "Pitch": "The perceived frequency of a sound, determining how high or low it seems.",
        "Volume": "Amplitude of the waveform, often expressed in decibels (dB).",
        "Timbre": "Tone color or texture of sound, distinguishing different sources.",
        "Envelope": "The evolution of a sound over time, broken into Attack, Decay, Sustain, Release (ADSR)."
    },
    "light": {
        "Hue": "The dominant wavelength of color (e.g. red, green, blue).",
        "Saturation": "Color purity – how free from gray the hue is.",
        "Brightness": "Perceived intensity or luminance of light.",
        "Pulse": "Fluctuations in brightness or intensity over time."
    },
    "genetics": {
        "Codon": "A sequence of three symbolic elements representing a perceptual unit.",
        "Mutation": "A symbolic or structural change to a codon or trait.",
        "Gene": "A repeatable symbolic pattern or functional unit across inputs.",
        "Epigenetics": "Feedback-driven regulation of codon expression without mutation."
    }
}

def get_term(domain: str, term: str) -> str:
    """Retrieve a term's definition."""
    return GLOSSARY.get(domain, {}).get(term, "Definition not found.")

def search_term(term: str) -> str:
    """Search all domains for a term."""
    for domain, terms in GLOSSARY.items():
        if term in terms:
            return f"{domain}: {terms[term]}"
    return "Term not found."

def get_all_terms() -> dict:
    return GLOSSARY
