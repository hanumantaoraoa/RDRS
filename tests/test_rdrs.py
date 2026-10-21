import pytest
from app.core.entropy import calculate_shannon_entropy


def test_entropy_evaluation_extremes():
    flat_data = b"A" * 1000
    variable_data = bytes(range(256))

    low_entropy = calculate_shannon_entropy(flat_data)
    high_entropy = calculate_shannon_entropy(variable_data)

    assert low_entropy == 0.0
    assert high_entropy > 7.5
