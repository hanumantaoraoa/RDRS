import os
import sys
import random
import string
from loguru import logger

# Add root folder path to lookups to pull configuration mappings safely
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from app.core.config import load_config
from app.core.entropy import calculate_shannon_entropy

def create_low_entropy_file(file_path: str, size_kb: int = 10) -> float:
    """Generates highly structured text data with low Shannon Entropy (~0.0 - 2.0)."""
    # Using repeating character sequences makes the data highly predictable
    content = ("DEATH_TO_RANSOMWARE_" * (size_kb * 50))[:size_kb * 1024].encode('utf-8')
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    entropy = calculate_shannon_entropy(file_path)
    logger.info(f"?? Low-Entropy File Generated: {os.path.basename(file_path)} | Size: {size_kb}KB | Calculated Entropy: {entropy:.2f}")
    return entropy

def create_high_entropy_file(file_path: str, size_kb: int = 10) -> float:
    """Generates highly randomized, pseudo-encrypted byte blocks with high Shannon Entropy (~7.5 - 8.0)."""
    # os.urandom provides cryptographically secure random bytes ideal for mimicking encryption
    content = os.urandom(size_kb * 1024)
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    entropy = calculate_shannon_entropy(file_path)
    logger.warning(f"?? High-Entropy File Generated: {os.path.basename(file_path)} | Size: {size_kb}KB | Calculated Entropy: {entropy:.2f}")
    return entropy

def main():
    try:
        config = load_config("rdrs/config.yaml")
        sandbox_dir = config.system.monitored_directory
    except Exception as e:
        logger.error(f"Failed to resolve system directory config: {e}")
        return

    print("==========================================================")
    print("      RDRS TELEMETRY ENTROPY PAYLOAD GENERATOR            ")
    print("==========================================================")
    
    # 1. Create a safe, low-entropy profile sample file
    low_path = os.path.join(sandbox_dir, "safe_user_profile.json")
    create_low_entropy_file(low_path, size_kb=15)
    
    # 2. Create a high-entropy payload mimicking an encrypted database dump
    high_path = os.path.join(sandbox_dir, "malicious_payload.locked")
    create_high_entropy_file(high_path, size_kb=15)

if __name__ == "__main__":
    main()
