"""Tests for active_inference module."""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from shunollo_core.cognition.active_inference import (
    InferenceState,
    ActiveInferenceAgent,
    create_active_inference_agent,
)


class MockImagination:
    """Mock autoencoder for testing."""
    
    def __init__(self, input_size=13):
        self.input_size = input_size
    
    def forward(self, x):
        return x * 0.9, None


class TestInferenceState:
    """Test InferenceState dataclass."""
    
    def test_creation(self):
        state = InferenceState(
            free_energy=0.5,
            accuracy=0.4,
            complexity=0.1,
            precision=1.0,
            action_taken="action1",
            converged=True,
            iterations=2,
            errors=[]
        )
        
        assert state.free_energy == 0.5
        assert state.accuracy == 0.4
        assert state.complexity == 0.1
        assert state.action_taken == "action1"
        assert state.converged
    
    def test_default_errors(self):
        state = InferenceState(
            free_energy=0.5,
            accuracy=0.4,
            complexity=0.1,
            precision=1.0,
            action_taken=None,
            converged=False,
            iterations=1
        )
        assert state.errors == []


class TestActiveInferenceAgentInit:
    """Test ActiveInferenceAgent initialization."""
    
    def test_default_initialization(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        assert agent.precision == 1.0
        assert agent.prior_precision == 1.0
        assert agent.input_size == 13
    
    def test_custom_parameters(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            learning_rate=0.2,
            prior_precision=2.0,
            input_size=20
        )
        
        assert agent.eta == 0.2
        assert agent.prior_precision == 2.0
        assert agent.input_size == 20
    
    def test_repr(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        repr_str = repr(agent)
        
        assert "ActiveInferenceAgent" in repr_str
        assert "precision" in repr_str
    
    def test_factory_function(self):
        mock_imagination = MockImagination()
        agent = create_active_inference_agent(
            imagination=mock_imagination,
            prior_precision=1.5
        )
        
        assert isinstance(agent, ActiveInferenceAgent)
        assert agent.prior_precision == 1.5


class TestCalculateFreeEnergy:
    """Test free energy calculation."""
    
    def test_zero_error_low_free_energy(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        observation = np.ones(10)
        prediction = np.ones(10)
        
        f, accuracy, complexity = agent.calculate_free_energy(observation, prediction)
        
        assert accuracy == 0.0
        assert complexity == 0.0
        assert f == 0.0
    
    def test_prediction_error_increases_accuracy(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        observation = np.ones(10)
        prediction = np.zeros(10)
        
        f, accuracy, complexity = agent.calculate_free_energy(observation, prediction)
        
        assert accuracy > 0
        assert f > 0
    
    def test_precision_affects_complexity(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            prior_precision=1.0
        )
        
        agent.precision = 2.0
        observation = np.ones(10)
        prediction = np.ones(10)
        
        f, accuracy, complexity = agent.calculate_free_energy(observation, prediction)
        
        assert complexity > 0
    
    def test_different_length_arrays(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        observation = np.ones(10)
        prediction = np.ones(5)
        
        f, accuracy, complexity = agent.calculate_free_energy(observation, prediction)
        
        assert isinstance(f, float)


class TestSelectAction:
    """Test action selection."""
    
    def test_no_action_below_threshold(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            convergence_threshold=0.5
        )
        
        action = agent.select_action(0.3, ["action1", "action2"])
        assert action is None
    
    def test_no_action_with_empty_list(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        action = agent.select_action(1.0, [])
        assert action is None
    
    def test_action_selected_above_threshold(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            convergence_threshold=0.1
        )
        
        action = agent.select_action(0.5, ["low", "medium", "high"])
        assert action in ["low", "medium", "high"]


class TestMinimizeSurprise:
    """Test the active inference loop."""
    
    def test_basic_inference_loop(self):
        mock_imagination = MockImagination(input_size=10)
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            input_size=10,
            max_iterations=3
        )
        
        signal = np.random.randn(10)
        state = agent.minimize_surprise(signal)
        
        assert isinstance(state, InferenceState)
        assert state.iterations <= 3
    
    def test_short_signal_raises(self):
        mock_imagination = MockImagination(input_size=10)
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            input_size=10
        )
        
        short_signal = np.random.randn(5)
        
        with pytest.raises(ValueError, match="Signal length"):
            agent.minimize_surprise(short_signal)
    
    def test_action_execution(self):
        mock_imagination = MockImagination(input_size=10)
        action_called = {"flag": False}
        
        def test_action():
            action_called["flag"] = True
        
        agent = ActiveInferenceAgent(
            imagination=mock_imagination,
            input_size=10,
            motor_registry={"test_action": test_action},
            convergence_threshold=0.0001
        )
        
        signal = np.random.randn(10) * 10
        state = agent.minimize_surprise(signal)
        
        if state.action_taken:
            assert action_called["flag"]
    
    def test_errors_collected(self):
        class FailingImagination:
            input_size = 10
            
            def forward(self, x):
                raise RuntimeError("Test error")
        
        agent = ActiveInferenceAgent(
            imagination=FailingImagination(),
            input_size=10
        )
        
        signal = np.random.randn(10)
        state = agent.minimize_surprise(signal)
        
        assert len(state.errors) > 0
        assert "Test error" in state.errors[0]


class TestRegisterAction:
    """Test action registration."""
    
    def test_register_action(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        def my_action():
            pass
        
        agent.register_action("my_action", my_action)
        
        assert "my_action" in agent.motor_registry


class TestSetPrecision:
    """Test precision setting."""
    
    def test_set_precision_within_bounds(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        agent.set_precision(5.0)
        assert agent.precision == 5.0
    
    def test_set_precision_clamped_low(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        agent.set_precision(0.01)
        assert agent.precision == agent.MIN_PRECISION
    
    def test_set_precision_clamped_high(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        agent.set_precision(100.0)
        assert agent.precision == agent.MAX_PRECISION


class TestReset:
    """Test agent reset."""
    
    def test_reset_clears_state(self):
        mock_imagination = MockImagination()
        agent = ActiveInferenceAgent(imagination=mock_imagination)
        
        agent.precision = 5.0
        agent._action_history.append({"action": "test"})
        
        agent.reset()
        
        assert agent.precision == 1.0
        assert len(agent._action_history) == 0


class TestActiveInferenceBiological:
    """Test biological constraints: Sleep, Fatigue, Metabolism."""
    
    class MockMemory:
        def __init__(self):
            self.optimized = False
            self.energy = 0.5
        
        def optimize(self, iterations: int):
            self.optimized = True
            self.energy /= (iterations + 1)
            return self.energy

    def test_sleep_restores_fatigue(self):
        """Sleep should reduce metabolic cost accumulation."""
        agent = ActiveInferenceAgent()
        agent.metabolic_cost = 1.0  # High fatigue
        
        agent.sleep(duration_cycles=10)
        
        assert agent.metabolic_cost < 1.0
        assert agent.metabolic_cost < 0.5
    
    def test_sleep_consolidates_memory(self):
        """Sleep should trigger memory optimization."""
        mock_mem = self.MockMemory()
        agent = ActiveInferenceAgent(memory_system=mock_mem)
        
        agent.sleep(duration_cycles=5)
        
        assert mock_mem.optimized
    
    def test_inference_increments_fatigue(self):
        """Thinking should make you tired (physicist constraint)."""
        agent = ActiveInferenceAgent(fatigue_rate=0.1)
        initial_cost = agent.metabolic_cost
        
        signal = np.random.randn(13)
        agent.minimize_surprise(signal)
        
        assert agent.metabolic_cost > initial_cost
        # Cost increments per iteration (3 default iterations)
        assert agent.metabolic_cost >= initial_cost + 0.3
    
    def test_fatigue_reduces_precision(self):
        """Fatigue should lower effective precision (Brain Fog)."""
        agent = ActiveInferenceAgent()
        agent.precision = 10.0
        agent.metabolic_cost = 1.0  # 100% fatigue
        
        # Effective precision = Precision / (1 + Fatigue)
        # = 10 / 2 = 5
        
        # We need to run one loop where precision is applied
        # But minimize_surprise updates precision dynamically.
        # Let's check internal state during execution by mocking
        
        # Easier: run loop and assert the FINAL precision implies fatigue effect
        # Or check that high fatigue results in lower precision than low fatigue for same input
        
        agent_fresh = ActiveInferenceAgent(prior_precision=10.0)
        agent_tired = ActiveInferenceAgent(prior_precision=10.0)
        agent_tired.metabolic_cost = 9.0 # Extreme fatigue (div by 10)
        
        signal = np.zeros(13) # Perfect prediction -> High Precision
        
        s1 = agent_fresh.minimize_surprise(signal)
        s2 = agent_tired.minimize_surprise(signal)
        
        # Fresh agent should have higher precision
        assert s1.precision > s2.precision
