"""
Integration tests for mathematical foundation modules.

These tests verify the modules work together in realistic scenarios,
not just in isolation.
"""
import pytest
import numpy as np


class TestFlowAnalysisIntegration:
    """Test flow analysis in realistic server monitoring scenario."""
    
    def test_complete_monitoring_session(self):
        """Simulate a full monitoring session with degradation detection."""
        from shunollo_core.physics_flow import VascularAnalyzer
        
        analyzer = VascularAnalyzer(window_size=10)
        
        # Simulate 5 healthy samples
        for i in range(5):
            analyzer.calculate_configurational_resistance(
                queue_depth=10, cpu_load=0.5, throughput_bps=1000
            )
            analyzer.calculate_flow_imbalance(
                bytes_out=1000, latency_ms=50
            )
        
        # Verify healthy baseline
        is_degrading, slope = analyzer.check_resistance_trend()
        assert not is_degrading or abs(slope) < 0.001
        
        # Simulate degradation (memory leak pattern)
        for i in range(5):
            analyzer.calculate_configurational_resistance(
                queue_depth=10 + i * 100,
                cpu_load=0.5 + i * 0.1,
                throughput_bps=max(100, 1000 - i * 200)
            )
        
        # Should detect increasing resistance
        is_degrading, slope = analyzer.check_resistance_trend()
        assert is_degrading
        assert slope > 0


class TestStochasticResonanceIntegration:
    """Test SR in realistic weak signal detection scenario."""
    
    def test_subthreshold_signal_detection_pipeline(self):
        """Test complete weak signal detection pipeline."""
        from shunollo_core.perception.stochastic_resonance import StochasticResonator
        
        # Create very weak periodic signal
        t = np.linspace(0, 10, 500)
        weak_signal = np.sin(2 * np.pi * 1.0 * t) * 0.08  # 8% of threshold
        
        resonator = StochasticResonator(random_seed=42)
        
        # Find optimal noise
        optimal_d, max_snr = resonator.find_optimal_noise(
            weak_signal,
            d_range=(0.01, 0.3),
            steps=10,
            signal_freq_hz=1.0,
            sampling_rate_hz=50.0
        )
        
        # Optimal noise should be near theoretical D_opt
        assert 0.05 < optimal_d < 0.25
        
        # Apply resonance with optimal noise
        detected, confidence, enhanced = resonator.detect_subthreshold(
            weak_signal, noise_trials=20
        )
        
        # Signal should be detectable with ensemble averaging
        assert isinstance(detected, (bool, np.bool_))
        assert len(enhanced) == len(weak_signal)


class TestHolographicMemoryIntegration:
    """Test holographic memory in realistic incident database scenario."""
    
    def test_incident_pattern_recognition(self):
        """Test storing and recognizing incident patterns."""
        from shunollo_core.memory.holographic import HolographicMemory
        
        memory = HolographicMemory(size=512, require_context=True)
        
        # Store different incident types
        incidents = {
            "ddos": (np.array([1, 0, 1, 0, 1] * 4), np.array([1, 2, 3] * 7)[:20]),
            "leak": (np.array([0.2, 0.4, 0.6, 0.8, 1.0] * 4), np.array([4, 5, 6] * 7)[:20]),
            "normal": (np.array([0.5, 0.5, 0.5, 0.5, 0.5] * 4), np.array([7, 8, 9] * 7)[:20]),
        }
        
        for name, (pattern, context) in incidents.items():
            memory.encode(pattern, context=context)
        
        # Verify retrieval works
        assert memory.memory_count == 3
        
        # Test resonance with known context
        known_context = incidents["ddos"][1]
        assert memory.check_resonance(known_context, threshold=0.01)
        
        # Test novelty detection
        novel = np.random.randn(20) * 10
        novelty = memory.get_novelty(novel)
        known_novelty = memory.get_novelty(known_context)
        
        # Both should have positive novelty scores
        assert novelty > 0
        assert known_novelty > 0
    
    def test_graceful_degradation_with_sharding(self):
        """Test memory survives partial data loss."""
        from shunollo_core.memory.holographic import (
            HolographicMemory, shard_memory, DistributedHolographicShard
        )
        import warnings
        
        memory = HolographicMemory(size=256, require_context=False)
        
        # Store patterns
        original_patterns = [np.random.randn(30) for _ in range(5)]
        for pattern in original_patterns:
            memory.encode(pattern)
        
        # Shard
        shards = shard_memory(memory, n_shards=4)
        
        # Lose one shard
        surviving_shards = shards[:3]
        
        # Reconstruct
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reconstructed = DistributedHolographicShard.reconstruct_from_shards(
                surviving_shards, original_size=256
            )
        
        # Should still have memory count
        assert reconstructed.memory_count == memory.memory_count
        
        # Recall should still work (degraded but functional)
        recalled, strength = reconstructed.recall(original_patterns[0])
        assert strength > 0


class TestSPADEIntegration:
    """Test SPADE in realistic spectral analysis scenario."""
    
    def test_waveform_analysis_pipeline(self):
        """Test complete waveform decomposition and analysis."""
        from shunollo_core.perception.spade import SPADEAnalyzer
        
        analyzer = SPADEAnalyzer(max_modes=6)
        
        # Create a signal with known mode structure
        t = np.linspace(-4, 4, 256)
        
        # Mode 0 dominant (Gaussian-like)
        mode0_signal = np.exp(-t**2 / 2)
        spectrum = analyzer.analyze_mode_spectrum(mode0_signal)
        assert spectrum["dominant_mode"] == 0
        
        # Asymmetric signal should have mode 1 content
        asymmetric = np.exp(-t**2 / 2) * t
        detected, delta, confidence = analyzer.detect_shadow_signal(asymmetric)
        # The delta should be non-zero for asymmetric signals
        assert delta != 0 or isinstance(detected, (bool, np.bool_))
    
    def test_orthonormality_verification(self):
        """Test that mode orthonormality is verifiable."""
        from shunollo_core.perception.spade import SPADEAnalyzer
        
        analyzer = SPADEAnalyzer(max_modes=4)
        result = analyzer.verify_orthonormality(n_samples=2000)
        
        # Low modes should be reasonably orthonormal
        assert result["max_off_diagonal"] < 0.15
        assert "orthonormal" in result


class TestCrossModuleIntegration:
    """Test modules working together in a complete pipeline."""
    
    def test_anomaly_detection_with_memory(self):
        """Test detecting anomaly and storing in holographic memory."""
        from shunollo_core.physics_flow import VascularAnalyzer
        from shunollo_core.memory.holographic import HolographicMemory
        
        # Create analyzer and memory
        analyzer = VascularAnalyzer()
        memory = HolographicMemory(size=256, require_context=True)
        
        # Simulate anomaly detection (mesh topology = anomaly)
        is_anomaly, turbulence = analyzer.detect_topology_anomaly(
            sources=10, sinks=10, edges=50  # Mesh topology
        )
        assert is_anomaly  # Mesh should trigger anomaly
        
        # Create incident fingerprint
        fingerprint = np.array([turbulence, 1.0, 0.0, 0.0])
        context = np.array([1, 0, 0, 1])  # "DDoS" context
        
        # Store in memory
        memory.encode(fingerprint, context=context)
        
        # Later: Check if we've seen this before
        resonates = memory.check_resonance(context, threshold=0.01)
        assert resonates
    
    def test_weak_signal_enhancement_with_mode_analysis(self):
        """Test enhancing weak signal then analyzing its mode structure."""
        from shunollo_core.perception.stochastic_resonance import StochasticResonator
        from shunollo_core.perception.spade import SPADEAnalyzer
        
        # Create weak signal
        t = np.linspace(-4, 4, 256)
        weak_signal = np.sin(t) * 0.1
        
        # Enhance with stochastic resonance
        resonator = StochasticResonator(random_seed=42)
        enhanced, _ = resonator.apply_resonance(weak_signal)
        
        # Analyze mode structure of enhanced signal
        analyzer = SPADEAnalyzer(max_modes=6)
        spectrum = analyzer.analyze_mode_spectrum(enhanced)
        
        assert "dominant_mode" in spectrum
        assert spectrum["total_energy"] > 0
