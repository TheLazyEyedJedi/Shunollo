"""
Gustatory Cortex (The Sense of Taste)
-------------------------------------
Biological Role: Chemical analysis of ingested matter (Data Payloads) for toxicity.
                 Bitter = High Entropy (Alkaloids/Encrypted). 
                 Sweet = Low Entropy (Glucose/Text). 
                 Sour = Structured Acid (Code/SQL).

Cybernatic Role: Agnostic Content Analysis.
                 "Tasting" the raw byte stream to detect format anomalies.
                 This is protocol-agnostic (works on Files, Packets, or Memory buffers).
"""
import string

def taste_payload(payload_bytes: bytes) -> dict:
    """
    Analyzes the 'Flavor' of the payload.
    """
    if not payload_bytes:
        return {"flavor": "bland", "toxicity": 0.0}

    # 1. Texture Analysis (Entropy Proxy)
    # Count printable characters
    printable = sum(1 for b in payload_bytes if chr(b) in string.printable)
    ratio = printable / len(payload_bytes)

    flavor = "unknown"
    toxicity = 0.0

    # 2. Flavor Classification
    if ratio > 0.9:
        # High text content -> "Sweet" (HTML, JSON, Text)
        flavor = "sweet"
        
        # Check for "Sour" (Code Injection)
        decoded = payload_bytes.decode('utf-8', errors='ignore').lower()
        if any(x in decoded for x in ["select", "union", "drop", "alert(", "<script"]):
             flavor = "sour" # Acidic/Corrosive (Code)
             toxicity = 0.8
             
    elif ratio < 0.3:
        # High binary content -> "Bitter" (Executable, Encrypted)
        flavor = "bitter"
        toxicity = 0.5 # Potentially toxic (Malware? Shellcode?)
    else:
        # Mixed -> "Umami" (Rich/Complex)
        flavor = "umami"
        toxicity = 0.1

    return {
        "flavor": flavor,
        "toxicity": toxicity,
        "texture_ratio": ratio
    }
