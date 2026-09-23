"""Versioned, lossless bounded integer-count channel; no domain semantics."""
from io import BytesIO
import numpy as np
from PIL import Image

MAPPING_VERSION = 'count-image-u16-v1'
MAX_BINS = 6000


def encode_counts(counts):
    """Encode 1..6000 unsigned 16-bit counts as a one-row grayscale PNG.

    The caller owns time units, coverage and source evidence. Zero encodes a
    count, not proof of observation coverage. No implicit clipping occurs.
    """
    values = list(counts)
    if not 1 <= len(values) <= MAX_BINS or any(type(n) is not int or not 0 <= n <= 65535 for n in values):
        raise ValueError('Expected 1..6000 unsigned 16-bit integer counts')
    output = BytesIO()
    Image.fromarray(np.array([values], dtype=np.uint16)).save(output, format='PNG')
    return output.getvalue()


def decode_counts(data, *, expected_bins):
    """Recover integer counts, rejecting incompatible or oversized artifacts."""
    if type(expected_bins) is not int or not 1 <= expected_bins <= MAX_BINS:
        raise ValueError('Invalid expected bin count')
    if not isinstance(data, bytes) or len(data) > 1024*1024:
        raise ValueError('Expected bounded PNG bytes')
    with Image.open(BytesIO(data)) as image:
        if image.format != 'PNG' or image.size != (expected_bins, 1) or image.mode not in ('I', 'I;16'):
            raise ValueError('Incompatible count image')
        values = np.asarray(image).reshape(-1).tolist()
    if any(not 0 <= n <= 65535 for n in values):
        raise ValueError('Count out of range')
    return values
