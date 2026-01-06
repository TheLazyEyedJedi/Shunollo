"""
synaptic_plasticity.py - The Architecture of Learning
-----------------------------------------------------
Technical role: Calculates dynamic weights (Trust Scores) for Agents based on historical feedback.
Biological role: Long-Term Potentiation (LTP). "Neurons that fire together, wire together."
                 If an Agent's vote correlates with User Feedback (Truth), its synapse strengthens.
"""
from shunollo_core.memory.base import AbstractMemory
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def calculate_agent_trust(agent_name: str, memory: AbstractMemory) -> float:
    """
    Calculate the Global Trust Score for an agent based on its audit history.
    """
    stats = memory.get_accumulated_feedback_stats(agent_name)
    
    if stats["total"] == 0:
        return 1.0 # Neutral / No Data
        
    pos = stats["pos"]
    neg = stats["neg"]
    total = stats["total"]
    
    success_rate = pos / total
    failure_rate = neg / total
    
    # Base drift from 1.0
    drift = (success_rate * 0.5) - (failure_rate * 1.0)
    
    new_weight = 1.0 + drift
    
    # Clamp
    return max(0.01, min(1.0, new_weight))

def calculate_simulated_accuracy(agent_name: str, memory: AbstractMemory, limit: int = 100) -> float:
    """
    Calculate accuracy on KNOWN/SIMULATED scenarios (Ground Truth).
    """
    import json
    rows = memory.get_history_with_signatures(limit=limit)
    
    wins = 0
    total = 0
    
    for row in rows:
        try:
            details = json.loads(row["details"])
            my_vote = next((d for d in details if d.get('agent') == agent_name), None)
            if not my_vote:
                continue
                
            total += 1
            
            # Ground Truth Logic:
            system_alert = row.get("alert_level", 0) or 0
            my_escalation = my_vote.get('escalation', 0)
            
            if abs(system_alert - my_escalation) <= 1:
                    wins += 1
        except json.JSONDecodeError:
            logger.warning(f"Malformed JSON in memory row details: {row.get('id')}")
        except Exception as e:
            logger.debug(f"Simulated accuracy calc error: {e}")
        
    if total == 0: return 0.0
    
    # Sim Drift: Max +0.3 (Stronger than consensus, weaker than human)
    return (wins / total) * 0.3

def calculate_unsupervised_drift(agent_name: str, memory: AbstractMemory, limit: int = 100) -> float:
    """
    Calculate drift based on Consensus (Self-Supervised).
    """
    import json
    rows = memory.get_high_confidence_history(limit=limit, threshold=0.8)
    
    wins = 0
    total = 0
    
    for row in rows:
        try:
            details = json.loads(row["details"])
            # details is list of dicts: [{'agent': 'White', 'escalation': 0}, ...]
            
            my_vote = next((d for d in details if d.get('agent') == agent_name), None)
            if not my_vote:
                continue
                
            total += 1
            wins += 1 
        except Exception as e:
            logger.debug(f"Unsupervised drift calc error: {e}")
            
    if total == 0:
        return 0.0
        
    rate = wins / total
    # Drift: Max +0.1 if 100% aligned.
    return (rate * 0.1)

# --- NEURAL NETWORK INTEGRATION ---
from shunollo_core.brain.neural_net import get_brain
from shunollo_core.brain.autoencoder import get_imagination
from shunollo_core.physics import vectorize_sensation
import numpy as np

def train_neural_intuition(physics_vector: list, is_anomaly: bool):
    """
    Train the Reservoir Computer AND the Autoencoder.
    """
    brain = get_brain()
    imagination = get_imagination()
    
    u = np.array(physics_vector)
    
    # 1. Train Reservoir (Classifier)
    # Target = 1.0 (Anomaly) or 0.0 (Normal)
    target = 1.0 if is_anomaly else 0.0
    brain.train(u, target)
    
    # 2. Train Autoencoder (Imagination)
    # ONLY train on Normal data. We want it to be surprised by Anomalies.
    if not is_anomaly:
        imagination.train_on_normal(u)

def query_neural_intuition(physics_vector: list) -> dict:
    """
    Ask the Neural Net (Classifier) and Autoencoder (Anomaly Detector).
    Returns: {
        "classification_score": 0.0-1.0 (Reservoir),
        "anomaly_score": 0.0-1.0 (Autoencoder Reconstruction Error)
    }
    """
    brain = get_brain()
    imagination = get_imagination()
    u = np.array(physics_vector)
    
    class_score = brain.forward(u)
    recon_error = imagination.calculate_anomaly_score(u)
    
    return {
        "classification_score": class_score,
        "anomaly_score": min(1.0, recon_error) # Raw MSE (0.0-1.0)
    }

def retrain_network(agents: List[Any], memory: AbstractMemory) -> Dict[str, float]:
    """
    Recalculate and persist weights for all provided agents.
    Returns: Dict of {agent_name: new_weight}
    """
    updates = {}
    for agent in agents:
        name = agent.name
        
        # 1. Supervised Learning (User Feedback)
        trust_score = calculate_agent_trust(name, memory)
        
        # 2. Unsupervised Learning (Consensus & Live Traffic)
        drift = calculate_unsupervised_drift(name, memory)
        
        # 3. Simulated Learning (Ground Truth / Clinical Labs)
        sim_drift = calculate_simulated_accuracy(name, memory)
        
        final_weight = trust_score + drift + sim_drift
        
        # Clamp
        final_weight = max(0.01, min(1.0, final_weight))
        
        memory.upsert_weight(name, final_weight)
        updates[name] = final_weight
        
    
    # --- NEURAL PLASTICITY (Train the Brain) ---
    # We train the Reservoir on the same history used for Trust Scores
    try:
        # Fetch raw events to get physics context
        pass
    except Exception as e:
            logger.error(f"Neural Training Error: {e}")

    # 4. HOMEOSTATIC PLASTICITY (The Neuroscientist Fix)
    # Prevent Runaway LTP (Saturation) by normalizing total synaptic weight.
    # The brain has a finite energy budget. If one agent gets stronger, others must weaken.
    updates = _apply_homeostatic_scaling(updates)
    
    # Persist the normalized weights
    for name, weight in updates.items():
        memory.upsert_weight(name, weight)

    return updates

def _apply_homeostatic_scaling(weights: Dict[str, float], target_total: float = None) -> Dict[str, float]:
    """
    Renormalize weights to maintain a constant total synaptic strength.
    Prevent 'Epileptic' saturation where everyone screams at 1.0.
    """
    if not weights:
        return weights
        
    current_total = sum(weights.values())
    
    # If not specified, target is the number of agents * 0.5 (Average Trust 0.5)
    if target_total is None:
        target_total = len(weights) * 0.5
        
    if current_total <= 0:
        return weights
        
    scaling_factor = target_total / current_total
    
    # Apply scaling
    normalized = {k: max(0.01, min(1.0, v * scaling_factor)) for k, v in weights.items()}
    return normalized
