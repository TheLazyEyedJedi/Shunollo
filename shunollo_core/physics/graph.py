"""
Shunollo Graph Physics
======================
Physics of graph optimization and constraints.
Handles Factor Graphs for memory consistency.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional

class FactorGraph:
    """
    Simple Factor Graph for constraint-based episodic memory optimization.
    Enforces consistency between connected memories.
    """
    def __init__(self):
        self.nodes: Dict[int, dict] = {} 
        self.factors: List[dict] = []
        self._node_id = 0
    
    def add_node(self, state: list, timestamp: float = 0.0) -> int:
        node_id = self._node_id
        self.nodes[node_id] = {
            'state': np.array(state, dtype=float),
            'timestamp': timestamp,
            'confidence': 1.0,
        }
        self._node_id += 1
        return node_id
    
    def add_temporal_constraint(self, node_a: int, node_b: int, expected_delta: list = None):
        if expected_delta is None: expected_delta = []
        self.factors.append({
            'type': 'temporal',
            'nodes': [node_a, node_b],
            'params': {'delta': np.array(expected_delta) if expected_delta else None}
        })
    
    def add_similarity_constraint(self, node_a: int, node_b: int, max_distance: float = 0.5):
        self.factors.append({
            'type': 'similarity',
            'nodes': [node_a, node_b],
            'params': {'max_dist': max_distance}
        })
    
    def compute_energy(self) -> float:
        total = 0.0
        for factor in self.factors:
            node_ids = factor['nodes']
            if not all(nid in self.nodes for nid in node_ids): continue
            states = [self.nodes[nid]['state'] for nid in node_ids]
            
            if factor['type'] == 'temporal':
                delta = factor['params']['delta']
                if delta is None: delta = np.zeros_like(states[0])
                diff = states[1] - states[0]
                residual = np.linalg.norm(diff - delta)
                total += residual ** 2
            elif factor['type'] == 'similarity':
                dist = np.linalg.norm(states[0] - states[1])
                max_dist = factor['params']['max_dist']
                residual = max(0, dist - max_dist)
                total += residual ** 2
        return total
    
    def optimize(self, iterations: int = 10, learning_rate: float = 0.1) -> float:
        for _ in range(iterations):
            gradients = {nid: np.zeros_like(self.nodes[nid]['state']) for nid in self.nodes}
            for factor in self.factors:
                node_ids = factor['nodes']
                if not all(nid in self.nodes for nid in node_ids): continue
                nid_a, nid_b = node_ids[0], node_ids[1]
                vec_a, vec_b = self.nodes[nid_a]['state'], self.nodes[nid_b]['state']
                
                if factor['type'] == 'temporal':
                    delta = factor['params']['delta']
                    if delta is None: delta = np.zeros_like(vec_a)
                    error_vec = vec_b - vec_a - delta
                    grad = 2.0 * error_vec
                    gradients[nid_b] += grad
                    gradients[nid_a] -= grad
                    
                elif factor['type'] == 'similarity':
                    diff = vec_a - vec_b
                    dist = np.linalg.norm(diff)
                    max_dist = factor['params']['max_dist']
                    if dist > max_dist and dist > 1e-9:
                        u = dist - max_dist
                        dE_du = 2.0 * u
                        du_da = diff / dist
                        grad = dE_du * du_da
                        gradients[nid_a] += grad
                        gradients[nid_b] -= grad
            
            for nid in self.nodes:
                self.nodes[nid]['state'] -= learning_rate * gradients[nid]
        return self.compute_energy()
    
    def get_trajectory(self) -> list:
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x['timestamp'])
        return [(n['timestamp'], n['state'].tolist()) for n in sorted_nodes]
