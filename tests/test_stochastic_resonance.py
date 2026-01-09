"""Tests for stochastic_resonance module."""
import pytest
import numpy as np
from shunollo_core.perception.stochastic_resonance import (
    StochasticResonator,
    create_resonator,
    STANDARD_BARRIER_HEIGHT,
    MIN_DT,
    MAX_DT,
)


class TestStochasticResonatorInit:
    """Test StochasticResonator initialization."""
    
    def test_default_initialization(self):
        sr = StochasticResonator()
        assert sr.delta_v == STANDARD_BARRIER_HEIGHT
        assert sr.d_opt == STANDARD_BARRIER_HEIGHT / 2
        assert sr.threshold == 0.5
    
    def test_custom_barrier_height(self):
        sr = StochasticResonator(barrier_height=0.5)
        assert sr.delta_v == 0.5
        assert sr.d_opt == 0.25
    
    def test_invalid_barrier_height_raises(self):
        with pytest.raises(ValueError, match="barrier_height must be positive"):
            StochasticResonator(barrier_height=0)
        
        with pytest.raises(ValueError, match="barrier_height must be positive"):
            StochasticResonator(barrier_height=-0.1)
    
    def test_reproducible_with_seed(self):
        signal = np.sin(np.linspace(0, 4 * np.pi, 100)) * 0.1
        
        sr1 = StochasticResonator(random_seed=42)
        output1, _ = sr1.apply_resonance(signal)
        
        sr2 = StochasticResonator(random_seed=42)
        output2, _ = sr2.apply_resonance(signal)
        
        np.testing.assert_array_equal(output1, output2)
    
    def test_repr(self):
        sr = StochasticResonator()
        repr_str = repr(sr)
        assert "StochasticResonator" in repr_str
        assert "delta_v" in repr_str
    
    def test_factory_function(self):
        sr = create_resonator(barrier_height=0.5)
        assert isinstance(sr, StochasticResonator)
        assert sr.delta_v == 0.5


class TestBistablePotential:
    """Test bistable potential functions."""
    
    def test_potential_minima(self):
        sr = StochasticResonator()
        x = np.array([-1.0, 0.0, 1.0])
        u = sr.bistable_potential(x)
        
        assert u[0] == pytest.approx(-0.25)
        assert u[1] == pytest.approx(0.0)
        assert u[2] == pytest.approx(-0.25)
    
    def test_potential_gradient_at_equilibrium(self):
        sr = StochasticResonator()
        x = np.array([-1.0, 0.0, 1.0])
        grad = sr.potential_gradient(x)
        
        assert grad[0] == pytest.approx(0.0)
        assert grad[1] == pytest.approx(0.0)
        assert grad[2] == pytest.approx(0.0)


class TestApplyResonance:
    """Test apply_resonance method."""
    
    def test_output_shape(self):
        sr = StochasticResonator(random_seed=42)
        signal = np.ones(100) * 0.1
        output, noise = sr.apply_resonance(signal)
        
        assert output.shape == (100,)
        assert noise.shape == (100,)
    
    def test_empty_signal(self):
        sr = StochasticResonator()
        output, noise = sr.apply_resonance(np.array([]))
        
        assert len(output) == 0
        assert len(noise) == 0
    
    def test_dt_too_small_raises(self):
        sr = StochasticResonator()
        signal = np.ones(100) * 0.1
        
        with pytest.raises(ValueError, match="dt=.* too small"):
            sr.apply_resonance(signal, dt=1e-8)
    
    def test_negative_noise_intensity_raises(self):
        sr = StochasticResonator()
        signal = np.ones(100) * 0.1
        
        with pytest.raises(ValueError, match="noise_intensity must be non-negative"):
            sr.apply_resonance(signal, noise_intensity=-0.1)
    
    def test_dt_warning(self):
        sr = StochasticResonator(random_seed=42)
        signal = np.ones(100) * 0.1
        
        with pytest.warns(UserWarning, match="may reduce accuracy"):
            sr.apply_resonance(signal, dt=1.5)
    
    def test_custom_noise_intensity(self):
        sr = StochasticResonator(random_seed=42)
        signal = np.sin(np.linspace(0, 4 * np.pi, 100)) * 0.1
        
        output_low, _ = sr.apply_resonance(signal, noise_intensity=0.01)
        sr.set_seed(42)
        output_high, _ = sr.apply_resonance(signal, noise_intensity=1.0)
        
        assert np.std(output_high) > np.std(output_low)


class TestDetectSubthreshold:
    """Test sub-threshold detection."""
    
    def test_basic_detection(self):
        sr = StochasticResonator(random_seed=42)
        signal = np.sin(np.linspace(0, 4 * np.pi, 100)) * 0.3
        
        detected, confidence, averaged = sr.detect_subthreshold(signal)
        
        assert isinstance(detected, (bool, np.bool_))
        assert 0 <= confidence <= 1
        assert len(averaged) == len(signal)
    
    def test_empty_signal(self):
        sr = StochasticResonator()
        detected, confidence, averaged = sr.detect_subthreshold(np.array([]))
        
        assert not detected
        assert confidence == 0.0
        assert len(averaged) == 0
    
    def test_invalid_noise_trials_raises(self):
        sr = StochasticResonator()
        signal = np.ones(100)
        
        with pytest.raises(ValueError, match="noise_trials must be >= 1"):
            sr.detect_subthreshold(signal, noise_trials=0)


class TestSpectralSNR:
    """Test spectral SNR computation."""
    
    def test_snr_calculation(self):
        sr = StochasticResonator(random_seed=42)
        t = np.linspace(0, 10, 1000)
        signal = np.sin(2 * np.pi * 1.0 * t) * 0.2
        
        snr = sr.compute_spectral_snr(
            signal,
            signal_freq_hz=1.0,
            sampling_rate_hz=100.0
        )
        
        assert isinstance(snr, float)


class TestFindOptimalNoise:
    """Test optimal noise finding."""
    
    def test_optimal_noise_in_range(self):
        sr = StochasticResonator(random_seed=42)
        t = np.linspace(0, 10, 500)
        signal = np.sin(2 * np.pi * 1.0 * t) * 0.1
        
        optimal_d, max_snr = sr.find_optimal_noise(
            signal,
            d_range=(0.05, 0.5),
            steps=10,
            signal_freq_hz=1.0,
            sampling_rate_hz=50.0
        )
        
        assert 0.05 <= optimal_d <= 0.5
        assert isinstance(max_snr, float)


class TestSetters:
    """Test setter methods."""
    
    def test_set_barrier_height(self):
        sr = StochasticResonator()
        sr.set_barrier_height(1.0)
        
        assert sr.delta_v == 1.0
        assert sr.d_opt == 0.5
    
    def test_set_barrier_height_invalid_raises(self):
        sr = StochasticResonator()
        
        with pytest.raises(ValueError, match="barrier_height must be positive"):
            sr.set_barrier_height(0)
    
    def test_set_seed(self):
        sr = StochasticResonator()
        sr.set_seed(123)
        
        signal = np.ones(50) * 0.1
        output1, _ = sr.apply_resonance(signal)
        
        sr.set_seed(123)
        output2, _ = sr.apply_resonance(signal)
        
        np.testing.assert_array_equal(output1, output2)
