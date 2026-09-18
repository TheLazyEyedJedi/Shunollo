import numpy as np
import pytest
from shunollo_core.brain.autoencoder import Autoencoder
from shunollo_core.brain.neural_net import LinearAssociativeMemory


@pytest.mark.parametrize('factory', [Autoencoder, LinearAssociativeMemory])
def test_constructor_preserves_global_random_stream(factory):
    np.random.seed(123)
    expected = np.random.random(4)
    np.random.seed(123)
    factory()
    np.testing.assert_array_equal(np.random.random(4), expected)


def test_autoencoder_invalid_values_match_sanitized_sample():
    dirty, clean = Autoencoder(), Autoencoder()
    x = np.full(18, .2)
    x[:3] = [np.nan, np.inf, -np.inf]
    sanitized = np.nan_to_num(x, nan=0, posinf=0, neginf=0)
    assert dirty.calculate_anomaly_score(x) == clean.calculate_anomaly_score(sanitized)
    dirty.train_on_normal(x)
    clean.train_on_normal(sanitized)
    for name in ('W_enc1', 'W_enc2', 'W_dec1', 'W_dec2'):
        np.testing.assert_array_equal(getattr(dirty, name), getattr(clean, name))
    assert np.isfinite(dirty.calculate_anomaly_score(np.ones(18)))


@pytest.mark.parametrize('factory', [Autoencoder, LinearAssociativeMemory])
@pytest.mark.parametrize('shape', [(18, 2), (1, 18), (17,), (18, 1, 1)])
def test_bad_shape_rejected_before_state_changes(factory, shape):
    model = factory()
    model.forward(np.ones(18))
    state = {k: v.copy() for k, v in vars(model).items() if isinstance(v, np.ndarray)}
    with pytest.raises(ValueError):
        model.forward(np.ones(shape))
    for name, value in state.items():
        np.testing.assert_array_equal(getattr(model, name), value)


@pytest.mark.parametrize('target', [np.nan, np.inf, -1, 2])
def test_invalid_target_does_not_mutate_reservoir(target):
    model = LinearAssociativeMemory(reservoir_size=8)
    with pytest.raises(ValueError):
        model.train(np.ones(18), target)
    assert not model.state.any() and not model.W_out.any() and model.bias == 0


@pytest.mark.parametrize('factory', [Autoencoder, LinearAssociativeMemory])
def test_checkpoint_roundtrip_adopts_dimensions(factory, tmp_path):
    original = (factory(input_size=4, reservoir_size=8)
                if factory is LinearAssociativeMemory else factory(input_size=4))
    x = np.full(4, .3)
    original.forward(x)
    path = tmp_path / 'model'
    original.save(path)
    restored = factory(input_size=18)
    restored.load(path)
    assert restored.input_size == 4
    if isinstance(original, LinearAssociativeMemory):
        original.reset(); restored.reset()
        assert restored.forward(x) == original.forward(x)
    else:
        np.testing.assert_array_equal(restored.forward(x)[0], original.forward(x)[0])


@pytest.mark.parametrize('factory', [Autoencoder, LinearAssociativeMemory])
@pytest.mark.parametrize('damage', ['missing', 'shape', 'nan'])
def test_bad_checkpoint_is_atomic(factory, damage, tmp_path):
    model = factory()
    model.forward(np.ones(18))
    state = {k: v.copy() for k, v in vars(model).items() if isinstance(v, np.ndarray)}
    path = tmp_path / 'model.npz'
    model.save(path)
    with np.load(path) as data:
        damaged = dict(data)
    last = 'W_dec2' if isinstance(model, Autoencoder) else 'state'
    if damage == 'missing':
        del damaged[last]
    elif damage == 'shape':
        damaged[last] = np.ones((2, 2))
    else:
        damaged[last] = np.full_like(damaged[last], np.nan)
    # A valid early field must not leak from a rejected checkpoint either.
    first = 'W_enc1' if isinstance(model, Autoencoder) else 'W_in'
    damaged[first] = damaged[first] + 1
    np.savez(path, **damaged)
    with pytest.raises((ValueError, KeyError)):
        model.load(path)
    for name, value in state.items():
        np.testing.assert_array_equal(getattr(model, name), value)
