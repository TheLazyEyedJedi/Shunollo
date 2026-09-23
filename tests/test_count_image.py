import pytest
from shunollo_core.perception.count_image import encode_counts, decode_counts


def test_full_range_boundaries():
    values = [0, 1, 255, 256, 65535]*1200
    assert decode_counts(encode_counts(values), expected_bins=len(values)) == values


@pytest.mark.parametrize('counts', [[], [True], [-1], [65536], [1.5], [0]*6001])
def test_invalid_counts_fail_without_clipping(counts):
    with pytest.raises(ValueError):
        encode_counts(counts)


def test_wrong_dimensions_and_budget():
    with pytest.raises(ValueError):
        decode_counts(encode_counts([1, 2]), expected_bins=1)
    with pytest.raises(ValueError):
        decode_counts(b'x'*(1024*1024+1), expected_bins=1)
