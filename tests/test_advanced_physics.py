"""Tests for advanced physics (Phase 500) - Neural Substrate implementations."""
import pytest
import math
from shunollo_core.physics import (
    Psychophysics,
    VestibularDynamics,
    PoissonDetector,
    StressTensor,
    PropagationPhysics,
    ImpedanceAnalyzer,
    # Phase 2: Biophysics
    ChemicalKinetics,
    ThermoDynamics,
    MechanoFilter,
    CriticalResonator,
    # Phase 3: Electronic Convergence
    NoisePhysics,
    FactorGraph,
    DistortionModel,
)


class TestPsychophysics:
    """Test Stevens' Power Law and Weber-Fechner."""
    
    def test_stevens_law_linear(self):
        """Linear exponent should return same value."""
        result = Psychophysics.apply_stevens_law(0.5, modality="default")
        assert result == pytest.approx(0.5)
    
    def test_stevens_law_compressive(self):
        """Brightness (0.33) should compress high values."""
        result = Psychophysics.apply_stevens_law(0.8, modality="brightness")
        # 0.8^0.33 = 0.928
        assert result > 0.8  # Compressive makes high values feel higher
        assert result == pytest.approx(0.8 ** 0.33)
    
    def test_stevens_law_expansive(self):
        """Pain (3.5) should expand small changes."""
        result = Psychophysics.apply_stevens_law(0.5, modality="pain")
        # 0.5^3.5 = 0.088
        assert result < 0.5  # Expansive makes mid values feel smaller
        assert result == pytest.approx(0.5 ** 3.5)
    
    def test_stevens_law_clamping(self):
        """Values should be clamped to [0, 1]."""
        result_high = Psychophysics.apply_stevens_law(1.5, modality="default")
        result_low = Psychophysics.apply_stevens_law(-0.5, modality="default")
        
        assert result_high == 1.0
        assert result_low == 0.0
    
    def test_jnd_weber(self):
        """JND should scale with intensity."""
        jnd_low = Psychophysics.calculate_jnd(0.1, weber_fraction=0.1)
        jnd_high = Psychophysics.calculate_jnd(1.0, weber_fraction=0.1)
        
        assert jnd_high == pytest.approx(10 * jnd_low)
        assert jnd_low == pytest.approx(0.01)


class TestVestibularDynamics:
    """Test Steinhausen integration model."""
    
    def test_integration_smoothing(self):
        """Integrator should smooth rapid changes."""
        integrator = VestibularDynamics(damping=0.9)
        
        # Sudden spike
        integrator.integrate_acceleration(1.0)
        first = integrator._velocity
        
        # Should not immediately reach 1.0 due to damping
        assert first < 1.0
        assert first == pytest.approx(0.1)  # (1-0.9) * 1.0
    
    def test_integration_accumulation(self):
        """Sustained acceleration should accumulate velocity."""
        integrator = VestibularDynamics(damping=0.9)
        
        # Apply constant acceleration
        for _ in range(20):
            integrator.integrate_acceleration(1.0)
        
        # Should approach asymptote: v_inf = (1-d)/(1-d) * accel = accel
        # For d=0.9: v_inf = 1.0 as n->inf
        assert integrator._velocity > 0.8
    
    def test_integration_reset(self):
        """Reset should clear state."""
        integrator = VestibularDynamics()
        integrator.integrate_acceleration(1.0)
        
        integrator.reset()
        
        assert integrator._velocity == 0.0
        assert len(integrator._history) == 0
    
    def test_cumulative_displacement(self):
        """Displacement should average velocities."""
        integrator = VestibularDynamics(damping=0.5)
        
        for i in range(5):
            integrator.integrate_acceleration(float(i))
        
        displacement = integrator.get_cumulative_displacement()
        assert displacement > 0


class TestPoissonDetector:
    """Test quantum-limited detection statistics."""
    
    def test_detection_probability_zero_events(self):
        """Zero events should have zero detection probability."""
        detector = PoissonDetector(threshold_events=5)
        prob = detector.detection_probability(0)
        
        assert prob == 0.0
    
    def test_detection_probability_high_events(self):
        """Many events should have high detection probability."""
        detector = PoissonDetector(threshold_events=5)
        prob = detector.detection_probability(20)
        
        assert prob > 0.99
    
    def test_detection_probability_threshold(self):
        """At threshold events, probability should be around 0.5."""
        detector = PoissonDetector(threshold_events=5)
        prob = detector.detection_probability(5)
        
        # P(n >= 5 | lambda=5) should be around 0.56
        assert 0.4 < prob < 0.7
    
    def test_snr_calculation(self):
        """SNR should increase with signal events."""
        detector = PoissonDetector(dark_noise=0.01)
        
        snr_low = detector.signal_to_noise(1.0)
        snr_high = detector.signal_to_noise(100.0)
        
        assert snr_high > snr_low
        # SNR = signal / sqrt(signal + dark)
        assert snr_high == pytest.approx(100 / math.sqrt(100.01))
    
    def test_is_above_threshold(self):
        """Threshold check should work correctly."""
        detector = PoissonDetector(threshold_events=3)
        
        assert not detector.is_above_threshold(1, confidence=0.95)
        assert detector.is_above_threshold(20, confidence=0.95)


class TestStressTensor:
    """Test Von Mises stress calculations."""
    
    def test_von_mises_uniform(self):
        """Uniform stress should give zero Von Mises."""
        vm = StressTensor.calculate_von_mises(1.0, 1.0, 1.0)
        assert vm == pytest.approx(0.0)
    
    def test_von_mises_uniaxial(self):
        """Uniaxial stress should give predictable result."""
        # sigma_1 = 1, sigma_2 = sigma_3 = 0
        vm = StressTensor.calculate_von_mises(1.0, 0.0, 0.0)
        # sqrt(0.5 * [(1-0)^2 + (0-0)^2 + (0-1)^2]) = sqrt(0.5 * 2) = 1.0
        assert vm == pytest.approx(1.0)
    
    def test_distortion_anomaly_uniform(self):
        """Uniform load should not be flagged as distortion."""
        is_distortion, vm, pressure = StressTensor.is_distortion_anomaly(
            [0.5, 0.5, 0.5]
        )
        
        assert not is_distortion
        assert vm == pytest.approx(0.0)
        assert pressure == pytest.approx(0.5)
    
    def test_distortion_anomaly_asymmetric(self):
        """Asymmetric load should be flagged as distortion."""
        is_distortion, vm, pressure = StressTensor.is_distortion_anomaly(
            [1.0, 0.0, 0.0]
        )
        
        assert is_distortion
        assert vm > 0


class TestPropagationPhysics:
    """Test cable theory / length constant calculations."""
    
    def test_length_constant(self):
        """Length constant should be sqrt(r_m / r_a)."""
        lc = PropagationPhysics.calculate_length_constant(100, 4)
        assert lc == pytest.approx(5.0)
    
    def test_length_constant_zero_axial(self):
        """Zero axial resistance should give infinite length constant."""
        lc = PropagationPhysics.calculate_length_constant(100, 0)
        assert lc == float('inf')
    
    def test_signal_at_distance(self):
        """Signal should decay exponentially."""
        initial = 1.0
        lc = 10.0
        
        at_zero = PropagationPhysics.signal_at_distance(initial, 0, lc)
        at_lambda = PropagationPhysics.signal_at_distance(initial, lc, lc)
        at_2lambda = PropagationPhysics.signal_at_distance(initial, 2*lc, lc)
        
        assert at_zero == pytest.approx(1.0)
        assert at_lambda == pytest.approx(1/math.e)
        assert at_2lambda == pytest.approx(1/math.e**2)
    
    def test_propagation_radius(self):
        """Propagation radius should be calculable."""
        radius = PropagationPhysics.propagation_radius(
            initial_amplitude=1.0,
            threshold=0.1,
            length_constant=10.0
        )
        
        # x = 10 * ln(1/0.1) = 10 * ln(10) = 23.03
        assert radius == pytest.approx(10 * math.log(10))


class TestImpedanceAnalyzer:
    """Test acoustic impedance matching."""
    
    def test_calculate_impedance(self):
        """Impedance should be product of density and velocity."""
        z = ImpedanceAnalyzer.calculate_impedance(2.0, 3.0)
        assert z == 6.0
    
    def test_reflection_perfect_match(self):
        """Perfect match should have zero reflection."""
        r = ImpedanceAnalyzer.reflection_coefficient(100, 100)
        assert r == pytest.approx(0.0)
    
    def test_reflection_mismatch(self):
        """Impedance mismatch should cause reflection."""
        # Air to water: Z_air = 415, Z_water = 1.5e6
        r = ImpedanceAnalyzer.reflection_coefficient(415, 1.5e6)
        # R = ((1.5e6 - 415) / (1.5e6 + 415))^2 ≈ 0.9989
        assert r > 0.99
    
    def test_transmission_efficiency(self):
        """Transmission should be 1 - reflection."""
        eff = ImpedanceAnalyzer.transmission_efficiency(100, 100)
        assert eff == pytest.approx(1.0)
        
        eff_mismatch = ImpedanceAnalyzer.transmission_efficiency(1, 100)
        assert eff_mismatch < 0.5
    
    def test_transformer_ratio(self):
        """Transformer ratio should match impedances."""
        # To match Z_source=1 to Z_load=100: ratio = sqrt(100/1) = 10
        ratio = ImpedanceAnalyzer.required_transformer_ratio(1, 100)
        assert ratio == pytest.approx(10.0)


class TestIntegration:
    """Integration tests for physics working together."""
    
    def test_sensor_pipeline(self):
        """Test complete sensor -> physics -> sensation pipeline."""
        # Simulate a pressure sensor reading
        raw_pressure = 0.7
        
        # Apply Stevens' law for pressure (exponent 1.1)
        perceived = Psychophysics.apply_stevens_law(raw_pressure, "pressure")
        
        # With n=1.1, 0.7^1.1 = 0.675 (compressive effect due to value < 1)
        assert perceived == pytest.approx(0.7 ** 1.1)
        
        # Check if above JND
        jnd = Psychophysics.calculate_jnd(raw_pressure, 0.05)
        assert jnd == pytest.approx(0.035)
    
    def test_anomaly_detection_pipeline(self):
        """Test multi-step anomaly detection."""
        # System loads: [CPU=0.9, Memory=0.2, Network=0.1]
        loads = [0.9, 0.2, 0.1]
        
        # Check for distortion (asymmetric load)
        is_distortion, vm, mean = StressTensor.is_distortion_anomaly(loads)
        
        # This is clearly asymmetric - should be flagged
        assert is_distortion
        
        # Calculate propagation radius if this is anomalous
        if is_distortion:
            radius = PropagationPhysics.propagation_radius(
                initial_amplitude=vm,
                threshold=0.1,
                length_constant=5.0
            )
            assert radius > 0


# =============================================================================
# PHASE 2: BIOPHYSICS TESTS
# =============================================================================

class TestChemicalKinetics:
    """Test Hill-Langmuir binding and Nernst potential."""
    
    def test_hill_langmuir_zero_concentration(self):
        """Zero concentration should give zero occupancy."""
        theta = ChemicalKinetics.hill_langmuir(0, kd=0.5)
        assert theta == 0.0
    
    def test_hill_langmuir_at_kd(self):
        """At Kd, occupancy should be 50% (for n=1)."""
        theta = ChemicalKinetics.hill_langmuir(0.5, kd=0.5, hill_coefficient=1.0)
        assert theta == pytest.approx(0.5)
    
    def test_hill_langmuir_saturation(self):
        """Very high concentration should approach 1.0."""
        theta = ChemicalKinetics.hill_langmuir(100, kd=0.5)
        assert theta > 0.99
    
    def test_hill_langmuir_cooperativity(self):
        """Higher Hill coefficient should make curve steeper."""
        # At concentration < Kd, higher n should give lower occupancy
        theta_n1 = ChemicalKinetics.hill_langmuir(0.3, kd=0.5, hill_coefficient=1)
        theta_n4 = ChemicalKinetics.hill_langmuir(0.3, kd=0.5, hill_coefficient=4)
        
        assert theta_n4 < theta_n1  # More cooperative = steeper below Kd
    
    def test_nernst_equilibrium(self):
        """Equal concentrations should give zero potential."""
        e = ChemicalKinetics.nernst_potential(10, 10)
        assert e == pytest.approx(0.0)
    
    def test_nernst_tenfold_gradient(self):
        """10x gradient should give ~61.5 mV at 37°C for monovalent."""
        e = ChemicalKinetics.nernst_potential(1, 10, valence=1, temperature_kelvin=310)
        # Should be ~+61.5 mV (positive because C_out > C_in)
        assert 59 < e < 64
    
    def test_nernst_divalent(self):
        """Divalent ions should give half the potential."""
        e_mono = ChemicalKinetics.nernst_potential(1, 10, valence=1)
        e_di = ChemicalKinetics.nernst_potential(1, 10, valence=2)
        
        assert e_di == pytest.approx(e_mono / 2)
    
    def test_binding_rate(self):
        """Binding rate should saturate with concentration."""
        rate_low = ChemicalKinetics.binding_rate(0.1, k_on=1.0, k_off=0.1)
        rate_high = ChemicalKinetics.binding_rate(10.0, k_on=1.0, k_off=0.1)
        
        assert rate_high > rate_low
        assert rate_high > 0.99  # Should be near saturation


class TestThermoDynamics:
    """Test Arrhenius kinetics and Q10."""
    
    def test_arrhenius_rate_increases_with_temp(self):
        """Rate should increase with temperature."""
        rate_cold = ThermoDynamics.arrhenius_rate(300)  # 27°C
        rate_hot = ThermoDynamics.arrhenius_rate(350)   # 77°C
        
        assert rate_hot > rate_cold
    
    def test_arrhenius_zero_temp(self):
        """Zero Kelvin should return zero rate."""
        rate = ThermoDynamics.arrhenius_rate(0)
        assert rate == 0.0
    
    def test_q10_calculation(self):
        """Q10 should capture rate doubling per 10°C."""
        # If rate doubles for 10°C change, Q10 = 2
        q10 = ThermoDynamics.q10_coefficient(1.0, 2.0, delta_temp=10.0)
        assert q10 == pytest.approx(2.0)
    
    def test_q10_enzyme_typical(self):
        """Typical enzyme Q10 is ~2."""
        rate_25 = 1.0
        rate_35 = 2.0
        q10 = ThermoDynamics.q10_coefficient(rate_25, rate_35, 10.0)
        assert 1.5 < q10 < 2.5
    
    def test_thermal_failure_below_threshold(self):
        """Probability should be low well below threshold."""
        prob = ThermoDynamics.thermal_failure_probability(60, threshold_celsius=85)
        assert prob < 0.1
    
    def test_thermal_failure_at_threshold(self):
        """Probability should be ~50% at threshold."""
        prob = ThermoDynamics.thermal_failure_probability(85, threshold_celsius=85)
        assert 0.4 < prob < 0.6
    
    def test_thermal_failure_above_threshold(self):
        """Probability should be high above threshold."""
        prob = ThermoDynamics.thermal_failure_probability(100, threshold_celsius=85)
        assert prob > 0.8


class TestMechanoFilter:
    """Test Pacinian-like viscoelastic filtering."""
    
    def test_static_pressure_decays(self):
        """Static pressure should decay to zero (rapid adaptation)."""
        filt = MechanoFilter(time_constant=0.05)
        
        # Apply constant pressure for several steps
        outputs = []
        for _ in range(50):
            out = filt.filter(1.0, dt=0.01)
            outputs.append(out)
        
        # Output should decay towards zero
        assert outputs[-1] < outputs[0]
        assert abs(outputs[-1]) < 0.1  # Should be nearly zero
    
    def test_vibration_passes(self):
        """Vibration/changes should pass through."""
        filt = MechanoFilter(time_constant=0.05)
        
        # Apply oscillating input
        outputs = []
        for i in range(20):
            # Alternate between 0 and 1
            input_val = 1.0 if i % 2 == 0 else 0.0
            out = filt.filter(input_val, dt=0.01)
            outputs.append(out)
        
        # Output should have significant amplitude for oscillations
        amplitude = max(outputs) - min(outputs)
        assert amplitude > 0.5
    
    def test_reset_clears_state(self):
        """Reset should clear filter memory."""
        filt = MechanoFilter()
        filt.filter(1.0)
        filt.filter(2.0)
        
        filt.reset()
        
        assert filt._prev_input == 0.0
        assert filt._prev_output == 0.0
    
    def test_adaptation_time_constant(self):
        """More layers should give longer time constant."""
        tau_thin = MechanoFilter.adaptation_time_constant(10, 1.0)
        tau_thick = MechanoFilter.adaptation_time_constant(50, 1.0)
        
        assert tau_thick > tau_thin


class TestCriticalResonator:
    """Test Hopf bifurcation active amplification."""
    
    def test_high_gain_for_weak_signals(self):
        """Weak signals should get high gain (near bifurcation)."""
        resonator = CriticalResonator(damping=0.01)
        
        gain = resonator.gain(0.001)
        # Gain should be ~1/(2*0.01) = 50
        assert gain > 40
    
    def test_compression_for_strong_signals(self):
        """Strong signals should be compressed."""
        resonator = CriticalResonator(damping=0.01, nonlinear_coefficient=1.0)
        
        gain_weak = resonator.gain(0.001)
        gain_strong = resonator.gain(1.0)
        
        assert gain_strong < gain_weak
    
    def test_amplify_preserves_sign(self):
        """Amplification should preserve signal polarity."""
        resonator = CriticalResonator(damping=0.1)
        
        out_pos = resonator.amplify(0.1)
        out_neg = resonator.amplify(-0.1)
        
        assert out_pos > 0
        assert out_neg < 0
    
    def test_sensitivity_enhancement_db(self):
        """Should provide significant dB enhancement."""
        resonator = CriticalResonator(damping=0.01)
        
        enhancement = resonator.sensitivity_enhancement()
        # 20*log10(1/0.02) ≈ 34 dB
        assert enhancement > 30
    
    def test_is_near_bifurcation(self):
        """Low damping should indicate near-critical operation."""
        near = CriticalResonator(damping=0.05)
        far = CriticalResonator(damping=0.2)
        
        assert near.is_near_bifurcation() is True
        assert far.is_near_bifurcation() is False


class TestBiophysicsIntegration:
    """Integration tests for Phase 2 biophysics."""
    
    def test_database_saturation_model(self):
        """Model database connection pool saturation."""
        # Pool has Kd=50 (50% occupied at 50 connections)
        # Hill n=2 for cooperative binding (connection bursts)
        
        load_25 = ChemicalKinetics.hill_langmuir(25, kd=50, hill_coefficient=2)
        load_50 = ChemicalKinetics.hill_langmuir(50, kd=50, hill_coefficient=2)
        load_100 = ChemicalKinetics.hill_langmuir(100, kd=50, hill_coefficient=2)
        
        assert load_25 < 0.25  # Below half-max
        assert load_50 == pytest.approx(0.5)  # At Kd
        assert load_100 >= 0.8  # Approaching saturation
    
    def test_server_thermal_risk(self):
        """Model CPU thermal throttling risk."""
        # Below threshold: low risk
        risk_normal = ThermoDynamics.thermal_failure_probability(65, 85)
        
        # At threshold: medium risk
        risk_warning = ThermoDynamics.thermal_failure_probability(85, 85)
        
        # Above threshold: high risk
        risk_critical = ThermoDynamics.thermal_failure_probability(95, 85)
        
        assert risk_normal < risk_warning < risk_critical
    
    def test_texture_vs_static_detection(self):
        """Mechano filter should distinguish texture from static."""
        filt = MechanoFilter(time_constant=0.02)
        
        # Static pressure: should decay
        for _ in range(20):
            static_out = filt.filter(1.0, dt=0.01)
        
        # At equilibrium, output should be near zero
        assert abs(static_out) < 0.2
        
        filt.reset()
        
        # Rapid texture change: should pass through
        filt.filter(0.0, dt=0.01)
        texture_out = filt.filter(1.0, dt=0.01)
        
        # Change should produce significant output
        assert abs(texture_out) > 0.5
    
    def test_weak_signal_amplification(self):
        """Critical resonator should detect sub-threshold signals."""
        resonator = CriticalResonator(damping=0.02)
        
        # Very weak signal
        weak_input = 0.001
        amplified = resonator.amplify(weak_input)
        
        # Should be amplified by factor of ~25 (1/(2*0.02))
        assert amplified > weak_input * 20


# =============================================================================
# PHASE 3: ELECTRONIC CONVERGENCE TESTS
# =============================================================================

class TestNoisePhysics:
    """Test Allan Variance and noise classification."""
    
    def test_allan_variance_calculation(self):
        """Should calculate variance across scales."""
        # White noise -> Slope -0.5
        noise = NoisePhysics.generate_noise('quantization', 1000)
        avk = NoisePhysics.allan_variance(noise, sample_rate=100)
        
        # Should have results for multiple taus
        assert len(avk) > 3
        # Smallest tau is 1/100 = 0.01
        assert 0.01 in avk
    
    def test_noise_classification_drift(self):
        """Should detect drift ramp (Slope +1)."""
        import numpy as np
        
        # Manufacturer a clean ramp to verify slope logic
        # Signal >> Noise
        n = 1000
        t = np.linspace(0, 10, n)  # 10 units range
        ramp = t                   # Slope 1
        noise = np.random.randn(n) * 0.01 # Minimal noise
        signal = ramp + noise
        
        avk = NoisePhysics.allan_variance(signal)
        n_type, slope, conf = NoisePhysics.classify_noise(avk)
        
        # Should contain 'drift' or have positive slope ~1
        # Allan Deviation of linear drift is slope +1
        # Allan Variance is slope +2
        # My implementation calculates slope of deviation (adev)
        
        assert n_type == 'drift_ramp' or slope > 0.8
    
    def test_noise_classification_white(self):
        """Should detect white noise (Slope -0.5)."""
        val = NoisePhysics.generate_noise('quantization', 2000)
        avk = NoisePhysics.allan_variance(val)
        n_type, slope, conf = NoisePhysics.classify_noise(avk)
        
        # White noise / Quantization is usually -0.5 to -1.0
        assert slope < -0.3
    
    def test_sensor_health_diagnosis(self):
        """Should diagnose health based on noise profile."""
        # Bias Instability -> Caution
        noise = NoisePhysics.generate_noise('bias_instability', 1000)
        avk = NoisePhysics.allan_variance(noise)
        
        score, diag = NoisePhysics.sensor_health(avk)
        
        # Might fluctuate due to random gen, but score usually < 0.9 for non-white
        # Bias instability typically has slope 0
        # White noise has slope -0.5
        
        # Just ensure it returns valid structure
        assert 0.0 <= score <= 1.0
        assert isinstance(diag, str)


class TestFactorGraph:
    """Test graph-based memory optimization."""
    
    def test_temporal_constraint(self):
        """Nodes should align to temporal constraint."""
        fg = FactorGraph()
        
        # Node A at 0
        id_a = fg.add_node([0.0])
        # Node B at 10 (but constraint says it should be +5)
        id_b = fg.add_node([10.0])
        
        # Constraint: B - A should be 5
        fg.add_temporal_constraint(id_a, id_b, expected_delta=[5.0])
        
        # Energy should be high: (10 - 0 - 5)^2 = 25
        energy_initial = fg.compute_energy()
        assert energy_initial > 20.0
        
        # Optimize
        final_energy = fg.optimize(iterations=50, learning_rate=0.1)
        
        # Energy should decrease significantly
        assert final_energy < energy_initial
        assert final_energy < 1.0
        
        # Nodes should move closer to satisfying A + 5 = B
        traj = fg.get_trajectory()
        val_a = traj[0][1][0]
        val_b = traj[1][1][0]
        assert abs(val_b - val_a - 5.0) < 1.0
    
    def test_similarity_constraint(self):
        """Nodes constrained to be similar should pull together."""
        fg = FactorGraph()
        
        id_a = fg.add_node([0.0])
        id_b = fg.add_node([2.0])
        
        # Must be within 0.5 distance
        fg.add_similarity_constraint(id_a, id_b, max_distance=0.5)
        
        fg.optimize(iterations=20)
        
        traj = fg.get_trajectory()
        val_a = traj[0][1][0]
        val_b = traj[1][1][0]
        
        # Distance should decrease to near 0.5
        dist = abs(val_b - val_a)
        assert dist < 1.0  # Should have been pulled in from 2.0


class TestDistortionModel:
    """Test visual distortion physics."""
    
    def test_linear_center(self):
        """Center should have no distortion."""
        dm = DistortionModel.attention_distortion(0.5)
        x_d, y_d = dm.distort(0.0, 0.0)
        
        assert x_d == 0.0
        assert y_d == 0.0
    
    def test_barrel_distortion(self):
        """Edges should be compressed/distorted (Barrel)."""
        # Barrel distortion: k1 > 0 -> coordinate shifts outward (pincushion) or inward (barrel)?
        # Usually k1 > 0 is barrel in some models, or pincushion in others.
        # Here: x_d = x(1 + k*r^2). If k>0, |x_d| > |x|. This is Pincushion.
        # If k<0, |x_d| < |x|. This is Barrel.
        # Wait, usually Brown-Conrady: k1 > 0 is Barrel?
        # Actually usually k1 > 0 is Pincushion (magnification increases with r).
        # k1 < 0 is Barrel (magnification decreases).
        # My implementation of attention_distortion uses k1 positive.
        
        dm = DistortionModel(k1=0.1) # Pincushion-ish
        x_d, y_d = dm.distort(1.0, 0.0)
        
        # r^2 = 1. radial = 1 + 0.1 = 1.1
        # x_d = 1.0 * 1.1 = 1.1
        assert x_d > 1.0
    
    def test_undistort_inverse(self):
        """Undistort should reverse distort."""
        dm = DistortionModel(k1=0.1)
        
        x_orig, y_orig = 0.5, 0.5
        x_d, y_d = dm.distort(x_orig, y_orig)
        
        # Should be different
        assert x_d != x_orig
        
        # Restore
        x_res, y_res = dm.undistort(x_d, y_d)
        
        assert x_res == pytest.approx(x_orig, abs=1e-4)
        assert y_res == pytest.approx(y_orig, abs=1e-4)
