"""
Olfactory Bulb (The Sense of Persistence)
-----------------------------------------
Biological Role: Smell (Chemoreception). The only sense that bypasses the Thalamus 
                 and goes directly to the Cortex/Amygdala. Linked to Memory and Emotion.

Cybernatic Role: Graph-based Persistent Threat Detection (APT).
                 Tracks "Scent Trails" (long-term connection patterns) using NetworkX.
                 Unlike visual/auditory (stateless/short-term), Smell is STATEFUL.

Logic:
- Nodes: IPs
- Edges: Connections (Weighted by frequency/duration)
- 'Miasma': A subgraph with high centrality or density (Botnet/C2).
"""
import networkx as nx
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger("OlfactoryBulb")

class OlfactoryBulb:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.max_nodes = 1000 # For memory safety
        self.decay_rate = 0.1
        self.last_prune = time.time()
        
    def sniff(self, source: str, target: str) -> Dict[str, float]:
        """
        Ingest a connection event and update the Scent Graph.
        Returns a 'Pheromone Profile' (Centrality/Risk).
        """
        src = source
        dst = target
        
        if not src or not dst:
            return {"miasma_score": 0.0}

        # 1. Update Graph State
        if not self.graph.has_node(src): self.graph.add_node(src, type="prospect")
        if not self.graph.has_node(dst): self.graph.add_node(dst, type="prospect")
        
        if self.graph.has_edge(src, dst):
            self.graph[src][dst]['weight'] += 1
            self.graph[src][dst]['last_seen'] = time.time()
        else:
            self.graph.add_edge(src, dst, weight=1, first_seen=time.time(), last_seen=time.time())

        # 2. Prune (Decay) if needed (Garbage Collection)
        if len(self.graph.nodes) > self.max_nodes:
             self._prune_graph()

        # 3. Analyze "Miasma" (Centrality)
        # We only run expensive centrality checks periodically or cheaply
        # Degree Centrality is cheap (O(1)).
        src_degree = self.graph.degree(src)
        
        # APT Logic: High Fan-Out (Scanner) or High Fan-In (Server)?
        # Or "Long Duration" (Beacon)?
        
        miasma = 0.0
        
        # Beacon Detection: Low weight edge but VERY consistent? 
        # Hard to do with just this simple graph, need time-series.
        # Let's focus on "Bad Hubs" (C2 Servers).
        
        if src_degree > 20: 
            miasma = 0.6 # High Degree = Loud Smell (Ammonia)
            
        # Recursive Centrality (Eigenvector) is too slow for per-packet.
        # We use Degree as a proxy for "Pungency".
        
        return {
            "pungency": min(1.0, src_degree / 50.0),
            "persistence": 1.0 # Placeholder for time-based logic
        }

    def _prune_graph(self):
        """Remove old scents."""
        now = time.time()
        remove_list = []
        for u, v, data in self.graph.edges(data=True):
            if now - data['last_seen'] > 300: # 5 mins TTL
                remove_list.append((u, v))
        
        self.graph.remove_edges_from(remove_list)
        
        # Remove isolated nodes
        iso = list(nx.isolates(self.graph))
        self.graph.remove_nodes_from(iso)
        logger.debug(f"Pruned graph. Nodes: {len(self.graph.nodes)}")

# Global Singleton
olfactory_bulb = OlfactoryBulb()
