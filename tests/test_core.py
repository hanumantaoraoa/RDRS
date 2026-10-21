import os
import pytest
from pathlib import Path
from rdrs.app.core.entropy import calculate_shannon_entropy
from rdrs.app.core.config import load_config

def test_entropy_of_zero_file(tmp_path):
    empty_file = tmp_path / "empty.dat"
    empty_file.write_bytes(b"")
    assert calculate_shannon_entropy(str(empty_file)) == 0.0

def test_entropy_high_value(tmp_path):
    # Construct a high random variance sequence mapping block
    random_bytes = bytes([int((x * 127) % 256) for x in range(2000)])
    rand_file = tmp_path / "random.dat"
    rand_file.write_bytes(random_bytes)
    assert calculate_shannon_entropy(str(rand_file)) > 5.0

def test_config_parsing_handling():
    with pytest.raises(FileNotFoundError):
        load_config("rdrs/non_existent_path_file.yaml")
