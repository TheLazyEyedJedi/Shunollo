"""
synaptic_tuner.py
-----------------
The Backpropagation Engine for Shunollo.
Responsible for loading learned weights from the database ("Long Term Memory")
and injecting them into the Physics Engine's configuration ("Reflexes").

Mappings:
    PHYSICS_ROUGHNESS_ENTROPY -> PhysicsConfig.ROUGHNESS_ENTROPY_WEIGHT
    PHYSICS_ROUGHNESS_JITTER  -> PhysicsConfig.ROUGHNESS_JITTER_WEIGHT
    PHYSICS_ROUGHNESS_ERROR   -> PhysicsConfig.ROUGHNESS_ERROR_WEIGHT
"""
from shunollo_core import physics
from shunollo_core.memory.base import AbstractMemory

# Map DB Key -> Config Attribute
SYNAPTIC_MAP = {
    "PHYSICS_ROUGHNESS_ENTROPY": "ROUGHNESS_ENTROPY_WEIGHT",
    "PHYSICS_ROUGHNESS_JITTER": "ROUGHNESS_JITTER_WEIGHT",
    "PHYSICS_ROUGHNESS_ERROR": "ROUGHNESS_ERROR_WEIGHT"
}

def initialize_synapses(memory: AbstractMemory):
    """
    Called at startup to synchronize the Physics Engine with learned weights.
    Implements a 'Self-Healing' mechanism: if weights are missing in DB,
    defaults are seeded.
    """
    print("[Synapse] Synchronizing Neural Weights...")
    
    updates = 0
    seeds = 0
    
    # 1. Load Long-Term Memory (All Weights)
    try:
        all_weights = {w['agent']: w['weight'] for w in memory.get_all_weights()}
    except Exception as e:
        print(f"[Synapse] Failed to load weights: {e}")
        all_weights = {}

    for db_key, config_attr in SYNAPTIC_MAP.items():
        # Get current learned weight
        weight = all_weights.get(db_key)
        
        if weight is None:
            # Seed default (First Run)
            default_val = getattr(physics.PhysicsConfig, config_attr)
            print(f"   [SEED] {db_key} not found. Seeding default: {default_val}")
            memory.upsert_weight(db_key, default_val)
            seeds += 1
        else:
            # Inject learned weight (Reflex Update)
            current_val = getattr(physics.PhysicsConfig, config_attr)
            if abs(current_val - weight) > 0.0001:
                setattr(physics.PhysicsConfig, config_attr, weight)
                print(f"   [UPDATE] {config_attr}: {current_val} -> {weight}")
                updates += 1
                
    if updates == 0 and seeds == 0:
        print("   [OK] Synapses stable. No drift detected.")
    elif seeds > 0:
        print(f"   [OK] Seeded {seeds} new synaptic pathways.")
    else:
        print(f"   [OK] Updated {updates} weights from long-term memory.")
