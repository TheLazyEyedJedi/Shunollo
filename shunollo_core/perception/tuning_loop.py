"""
tuning_loop.py - The Optimization Engine
----------------------------------------
Iterates through hyperparameter space (Physics Weights) to find the configuration
that maximizes F1-Score (Precision/Recall Balance).
"""
import itertools
import logging
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GridSearch")

class TuningParameter:
    def __init__(self, name: str, min_val: float, max_val: float, step: float):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        
    def generate_values(self) -> List[float]:
        """Generate range of values for this parameter."""
        values = []
        curr = self.min_val
        # Add epsilon to handle floating point inclusion
        while curr <= (self.max_val + 0.0001):
            values.append(round(curr, 4))
            curr += self.step
        return values

class GridSearch:
    def __init__(self, referee):
        self.referee = referee
        self.logger_callback = None
        
    def _log(self, msg: str):
        if self.logger_callback:
            self.logger_callback(msg)
        logger.info(msg)

    def optimize(self, parameters: List[TuningParameter]) -> Tuple[Dict[str, float], float]:
        """
        Run Grid Search over provided parameters.
        Returns (Best Configuration Dict, Best F1 Score).
        """
        self._log(f"Optimization Started for {len(parameters)} parameters.")
        
        # 1. Generate Grid
        param_names = [p.name for p in parameters]
        value_lists = [p.generate_values() for p in parameters]
        
        # Cartesian Product of all parameter values
        combinations = list(itertools.product(*value_lists))
        self._log(f"Generated {len(combinations)} test configurations.")
        
        best_score = -1.0
        best_config = {}
        
        # 2. Iterate and Evaluate
        for combo in combinations:
            # Construct configuration dict (e.g. {'ROUGHNESS': 0.2})
            config = dict(zip(param_names, combo))
            
            # Delegate to Referee (Dependency Injection)
            score = self.referee.evaluate_configuration(config)
            
            self._log(f"Tested {config} -> F1: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_config = config
                self._log(f"*** New Best Score: {best_score:.4f} ***")
                
        self._log(f"Optimization Complete. Best F1: {best_score:.4f}")
        return best_config, best_score
