"""Shared single-observation and checkpoint validation for neural models."""
import numpy as np


def sample_column(value, size):
    value = np.asarray(value, dtype=float)
    if value.shape not in ((size,), (size, 1)):
        raise ValueError(f"expected a single sample of shape ({size},) or ({size}, 1)")
    # Preserve the established inference policy consistently in loss/training.
    return np.nan_to_num(value.reshape(size, 1), nan=0., posinf=0., neginf=0.)


def validated_arrays(data, shapes):
    result = {}
    for name, shape in shapes.items():
        value = np.asarray(data[name], dtype=float)
        if min(shape) <= 0 or value.shape != shape or not np.isfinite(value).all():
            raise ValueError(f"invalid checkpoint array: {name}")
        result[name] = value.copy()
    return result
