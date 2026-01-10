import pytest
import numpy as np
import sys
import os

# Ensure we test the LOCAL physics code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

from shunollo_core.brain.neural_net import LinearAssociativeMemory, get_brain
from shunollo_core.learning.synaptic_plasticity import train_neural_intuition, query_neural_intuition
from shunollo_core.memory.base import AbstractMemory

# We need to patch the memory used by synaptic_plasticity because it expects imports that might not work cleanly 
# or we just rely on standard behavior. train_neural_intuition imports get_brain locally.
# So this should be safe.

class TestNeuroSymbolic:
    
    def test_reservoir_initialization(self):
        """Verify the brain initializes with correct matrix dimensions."""
        brain = LinearAssociativeMemory()
        assert brain.W_in.shape == (100, 18)
        assert brain.W_res.shape == (100, 100)
        assert brain.W_out.shape == (1, 100)
        
    def test_online_learning(self):
        """Verify the brain can learn to distinguish patterns."""
        brain = get_brain(reset=True)
        
        # 1. Create Patterns (18-dim)
        white_vec = [0.1] * 15 + [1.0, 0.0, 0.0]
        red_vec = [0.9] * 15 + [0.0, 1.0, 0.0]
        
        # 3. Train
        for _ in range(50):
            brain.train(np.array(red_vec), 1.0)
            brain.train(np.array(white_vec), 0.0)
            
        # 4. Predict
        res_white = brain.forward(np.array(white_vec))
        res_red = brain.forward(np.array(red_vec))
        
        print(f"Post-Train White: {res_white}")
        print(f"Post-Train Red: {res_red}")
        
        assert res_white["classification_score"] < 0.3, "Brain failed to learn Safety"
        assert res_red["classification_score"] > 0.7, "Brain failed to learn Danger"

    def test_interpolation(self):
        """Verify the brain generalizes to unseen data."""
        brain = get_brain(reset=True)
        
        vec_a = [0.1] * 18
        vec_b = [0.9] * 18
        
        brain.train(np.array(vec_a), 0.0)
        brain.train(np.array(vec_b), 1.0)
        
        # Test vector in between
        vec_mid = [0.5] * 18
        res = brain.forward(np.array(vec_mid))
        pred = res["classification_score"]
        
        # Should be between 0.1 and 0.9
        assert 0.1 < pred < 0.9
