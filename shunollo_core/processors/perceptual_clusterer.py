"""
temporal_clusterer.py – Groups stream events into cohesive "Temporal Clusters".
"""

import time
import uuid
import statistics
import json
from collections import defaultdict, Counter, deque
from typing import Dict, Any, List, Optional

class PerceptualClusterer:
    # 5 seconds of silence closes a cluster
    SILENCE_TIMEOUT = 5.0
    # 60 seconds max duration before forcing a split (keep clusters focused)
    MAX_DURATION = 60.0
    # Maximum closed clusters to retain in memory
    MAX_CLOSED_CLUSTERS = 1000

    def __init__(self):
        # Key: (src, dst) -> { "events": [], "start_ts": float, "last_ts": float, "id": str }
        self.active_clusters: Dict[tuple, Dict[str, Any]] = {}
        self.closed_clusters: deque = deque(maxlen=self.MAX_CLOSED_CLUSTERS)

    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Ingest a single event (stimulus) and route it to an active cluster.
        """
        # Extract Flow Key (Source -> Dest)
        # Supports agnostic 'stimulus' or legacy 'packet'
        stimulus = event.get("stimulus") or event.get("packet", {})
        
        # Agnostic Keying: If no src/dst, use generic 'source_id' or hash
        src = stimulus.get("src", stimulus.get("source_id", "unknown"))
        dst = stimulus.get("dst", stimulus.get("target_id", "unknown"))
        key = (src, dst)
        
        now = event.get("timestamp", time.time())

        # Check if we possess an active cluster for this key
        cluster = self.active_clusters.get(key)

        if cluster:
            # Check timeouts
            silence = now - cluster["last_ts"]
            duration = now - cluster["start_ts"]

            if silence > self.SILENCE_TIMEOUT or duration > self.MAX_DURATION:
                # Close it
                self._close_cluster(key)
                cluster = None # Reset
        
        # Create new if needed
        if not cluster:
            cluster = {
                "id": str(uuid.uuid4()),
                "flow_key": key,
                "start_ts": now,
                "last_ts": now,
                "events": []
            }
            self.active_clusters[key] = cluster

        # Add event
        cluster["events"].append(event)
        cluster["last_ts"] = now

    def flush(self) -> List[Dict[str, Any]]:
        """
        Check all active clusters for timeouts, force close if needed, 
        and return ALL newly closed clusters since last flush.
        """
        now = time.time()
        
        # Check active clusters for silence timeout
        keys_to_close = []
        for key, cls in self.active_clusters.items():
            if (now - cls["last_ts"]) > self.SILENCE_TIMEOUT:
                keys_to_close.append(key)
        
        for k in keys_to_close:
            self._close_cluster(k)
        
        # Return and clear the buffer of closed clusters
        results = list(self.closed_clusters)
        self.closed_clusters.clear()
        return results

    def _close_cluster(self, key: tuple) -> None:
        """
        Finalize a cluster: compute centroid, tags, signatures, and move to closed_list.
        """
        if key not in self.active_clusters:
            return

        raw = self.active_clusters.pop(key)
        events = raw["events"]
        if not events:
            return

        # 1. Compute Centroids
        avg_conf = statistics.mean([e.get("avg_confidence", 0) for e in events])
        avg_sound = statistics.mean([e.get("avg_sound_score", 0) for e in events])
        avg_light = statistics.mean([e.get("avg_light_score", 0) for e in events])
        
        # 2. Key Metadata
        src, dst = raw["flow_key"]
        
        # 3. Consensus (Who was the loudest hat?)
        hat_scores = defaultdict(list)
        for e in events:
            for agent_res in e.get("details", []):
                name = agent_res.get("agent")
                score = agent_res.get("score", 0)
                hat_scores[name].append(score)
        
        hat_consensus = {k: round(statistics.mean(v), 3) for k,v in hat_scores.items()}

        # 4. Signature / Tags Dominance
        all_tags = []
        for e in events:
            all_tags.extend(e.get("tags", []))
        
        dominant_tag = "unknown"
        if all_tags:
            dominant_tag = Counter(all_tags).most_common(1)[0][0]

        # 5. Representative Event
        sorted_events = sorted(events, key=lambda x: x.get("alert_level", 0), reverse=True)
        rep_event = sorted_events[0]
        rep_id = rep_event.get("correlation_id")

        # Size Summation (Agnostic 'volume')
        total_size = 0
        for e in events:
            s = e.get("stimulus") or e.get("packet", {})
            total_size += s.get("size", s.get("volume", 0))

        # Centroid Physics extraction relying on agnostic 'stimulus'
        def get_physics(evt, key, default=0.0):
            stim = evt.get("stimulus") or evt.get("packet", {})
            return stim.get(key, default)

        summary = {
            "cluster_id": raw["id"],
            "timestamp": raw["last_ts"], 
            "start_ts": raw["start_ts"],
            "end_ts": raw["last_ts"],
            "event_count": len(events),
            "avg_confidence": round(avg_conf, 3), 
            "alert_level": max([e.get("alert_level", 0) for e in events], default=0),
            "signature": "unknown", 
            "recommended_action": "monitor",
            "size": total_size,
            "payload": json.dumps({
                "src": src,
                "dst": dst,
                "dominant_tag": dominant_tag,
                "centroid_sound": round(avg_sound, 3),
                "centroid_light": round(avg_light, 3),
                "hat_consensus": hat_consensus,
                "representative_id": rep_id,
                
                # Basal Ganglia Physics
                "centroid_harmony": round(statistics.mean([get_physics(e, "harmony", 1.0) for e in events]), 3),
                "centroid_flux": round(statistics.mean([get_physics(e, "flux", 0.0) for e in events]), 3),
                "centroid_roughness": round(statistics.mean([get_physics(e, "roughness", 0.0) for e in events]), 3),
                "centroid_viscosity": round(statistics.mean([get_physics(e, "viscosity", 0.0) for e in events]), 3),
                "centroid_dissonance": round(statistics.mean([get_physics(e, "dissonance", 0.0) for e in events]), 3),
                "centroid_entropy": round(statistics.mean([get_physics(e, "entropy", 0.0) for e in events]), 3),
                "centroid_spatial_x": round(statistics.mean([get_physics(e, "spatial_x", 0.0) for e in events]), 3)
            })
        }
        
        self.closed_clusters.append(summary)
