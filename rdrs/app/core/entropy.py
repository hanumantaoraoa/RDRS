import math
import os


def calculate_shannon_entropy(data: bytes) -> float:
    """Computes Shannon Entropy of byte streams scaled from 0.0 to 8.0."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256

    for byte in data:
        counts[byte] += 1

    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy


def calculate_file_entropy(file_path: str, sample_size_bytes: int = 65536) -> float:
    """Reads the first chunk block allocation sample to determine complexity values safely."""
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return 0.0
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size_bytes)
            return calculate_shannon_entropy(chunk)
    except Exception:
        return 0.0
