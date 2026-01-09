"""Tests for physics_flow module."""
import pytest
import numpy as np
from shunollo_core.physics_flow import (
    VascularAnalyzer,
    get_vascular_analyzer,
    MIN_CPU_LOAD,
    MIN_THROUGHPUT,
    TURBULENCE_THRESHOLD,
)


class TestVascularAnalyzerInit:
    """Test VascularAnalyzer initialization."""
    
    def test_default_initialization(self):
        analyzer = VascularAnalyzer()
        assert analyzer.window_size == 100
        assert analyzer.baseline_bytes == 1000.0
        assert analyzer.baseline_latency == 100.0
    
    def test_custom_initialization(self):
        analyzer = VascularAnalyzer(
            window_size=50,
            baseline_bytes=2000.0,
            baseline_latency=50.0
        )
        assert analyzer.window_size == 50
        assert analyzer.baseline_bytes == 2000.0
        assert analyzer.baseline_latency == 50.0
    
    def test_invalid_window_size(self):
        with pytest.raises(ValueError, match="window_size must be positive"):
            VascularAnalyzer(window_size=0)
        
        with pytest.raises(ValueError, match="window_size must be positive"):
            VascularAnalyzer(window_size=-5)
    
    def test_repr(self):
        analyzer = VascularAnalyzer(window_size=50)
        repr_str = repr(analyzer)
        assert "VascularAnalyzer" in repr_str
        assert "window_size=50" in repr_str
    
    def test_factory_function(self):
        analyzer = get_vascular_analyzer(window_size=25)
        assert isinstance(analyzer, VascularAnalyzer)
        assert analyzer.window_size == 25


class TestConfigurationalResistance:
    """Test configurational resistance calculation."""
    
    def test_basic_calculation(self):
        analyzer = VascularAnalyzer()
        r_c = analyzer.calculate_configurational_resistance(
            queue_depth=10,
            cpu_load=0.5,
            throughput_bps=1000
        )
        assert r_c == pytest.approx(0.005)
    
    def test_zero_throughput_returns_infinity(self):
        analyzer = VascularAnalyzer()
        r_c = analyzer.calculate_configurational_resistance(
            queue_depth=10,
            cpu_load=0.5,
            throughput_bps=0.5
        )
        assert r_c == float('inf')
    
    def test_negative_queue_depth_raises(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="queue_depth cannot be negative"):
            analyzer.calculate_configurational_resistance(
                queue_depth=-1,
                cpu_load=0.5,
                throughput_bps=1000
            )
    
    def test_invalid_cpu_load_raises(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="cpu_load must be in"):
            analyzer.calculate_configurational_resistance(
                queue_depth=10,
                cpu_load=1.5,
                throughput_bps=1000
            )
    
    def test_negative_throughput_raises(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="throughput_bps cannot be negative"):
            analyzer.calculate_configurational_resistance(
                queue_depth=10,
                cpu_load=0.5,
                throughput_bps=-100
            )
    
    def test_zero_cpu_load_uses_minimum(self):
        analyzer = VascularAnalyzer()
        r_c = analyzer.calculate_configurational_resistance(
            queue_depth=100,
            cpu_load=0.0,
            throughput_bps=1000
        )
        expected = (100 * MIN_CPU_LOAD) / 1000
        assert r_c == pytest.approx(expected)


class TestFlowImbalance:
    """Test flow imbalance calculation."""
    
    def test_basic_calculation(self):
        analyzer = VascularAnalyzer(baseline_bytes=1000, baseline_latency=100)
        imbalance = analyzer.calculate_flow_imbalance(
            bytes_out=1000,
            latency_ms=100
        )
        assert imbalance == pytest.approx(0.0, abs=0.01)
    
    def test_high_throughput_low_latency(self):
        analyzer = VascularAnalyzer(baseline_bytes=1000, baseline_latency=100)
        imbalance = analyzer.calculate_flow_imbalance(
            bytes_out=10000,
            latency_ms=10
        )
        assert imbalance > 0
    
    def test_negative_bytes_raises(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="bytes_out cannot be negative"):
            analyzer.calculate_flow_imbalance(bytes_out=-100, latency_ms=50)
    
    def test_negative_latency_raises(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="latency_ms cannot be negative"):
            analyzer.calculate_flow_imbalance(bytes_out=100, latency_ms=-50)
    
    def test_history_accumulation(self):
        analyzer = VascularAnalyzer(window_size=5)
        for i in range(10):
            analyzer.calculate_flow_imbalance(bytes_out=100 * (i + 1), latency_ms=50)
        
        assert analyzer.get_integrated_imbalance() > 0
        assert analyzer.get_mean_imbalance() > 0


class TestTopologyAnomaly:
    """Test topology anomaly detection."""
    
    def test_tree_topology_is_normal(self):
        analyzer = VascularAnalyzer()
        is_anomalous, turbulence = analyzer.detect_topology_anomaly(
            sources=5, sinks=5, edges=9
        )
        assert not is_anomalous
        assert turbulence == pytest.approx(0.0)
    
    def test_mesh_topology_is_anomalous(self):
        analyzer = VascularAnalyzer()
        is_anomalous, turbulence = analyzer.detect_topology_anomaly(
            sources=5, sinks=5, edges=20
        )
        assert is_anomalous
        assert turbulence > TURBULENCE_THRESHOLD
    
    def test_single_node_returns_false(self):
        analyzer = VascularAnalyzer()
        is_anomalous, turbulence = analyzer.detect_topology_anomaly(
            sources=1, sinks=0, edges=0
        )
        assert not is_anomalous
        assert turbulence == 0.0
    
    def test_negative_values_raise(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="cannot be negative"):
            analyzer.detect_topology_anomaly(sources=-1, sinks=5, edges=10)


class TestResistanceTrend:
    """Test resistance trend detection."""
    
    def test_increasing_resistance(self):
        analyzer = VascularAnalyzer()
        for i in range(5):
            analyzer.calculate_configurational_resistance(
                queue_depth=10 * (i + 1),
                cpu_load=0.5,
                throughput_bps=1000
            )
        
        is_increasing, slope = analyzer.check_resistance_trend()
        assert is_increasing
        assert slope > 0
    
    def test_insufficient_history(self):
        analyzer = VascularAnalyzer()
        analyzer.calculate_configurational_resistance(
            queue_depth=10, cpu_load=0.5, throughput_bps=1000
        )
        
        is_increasing, slope = analyzer.check_resistance_trend()
        assert not is_increasing
        assert slope == 0.0


class TestReset:
    """Test reset functionality."""
    
    def test_reset_clears_history(self):
        analyzer = VascularAnalyzer()
        for i in range(5):
            analyzer.calculate_flow_imbalance(bytes_out=100, latency_ms=50)
            analyzer.calculate_configurational_resistance(
                queue_depth=10, cpu_load=0.5, throughput_bps=1000
            )
        
        assert analyzer.get_integrated_imbalance() > 0
        
        analyzer.reset()
        
        assert analyzer.get_integrated_imbalance() == 0.0


class TestUpdateBaselines:
    """Test baseline updates."""
    
    def test_update_baselines(self):
        analyzer = VascularAnalyzer()
        analyzer.update_baselines(bytes_baseline=5000, latency_baseline=200)
        
        assert analyzer.baseline_bytes == 5000
        assert analyzer.baseline_latency == 200
    
    def test_invalid_baselines_raise(self):
        analyzer = VascularAnalyzer()
        with pytest.raises(ValueError, match="Baselines must be positive"):
            analyzer.update_baselines(bytes_baseline=0, latency_baseline=100)
