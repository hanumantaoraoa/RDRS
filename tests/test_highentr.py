import os
import sys
from loguru import logger

# Add root folder path to lookups to pull configuration mappings safely
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from app.core.config import load_config
from app.core.entropy import calculate_shannon_entropy

def inject_high_entropy_payload(filename: str = "adversary_payload.crypto", size_kb: int = 50):
    """
    Generates a cryptographically random file to achieve high Shannon Entropy (~7.95+).
    Forces immediate high-entropy analytics weight rule validation in the RDRS pipeline.
    """
    logger.info("??? Resolving active RDRS system config workspace context...")
    try:
        config = load_config("rdrs/config.yaml")
        sandbox_dir = config.system.monitored_directory
    except Exception as e:
        logger.error(f"? Failed to locate configuration workspace mapping details: {e}")
        return

    # Establish full target file path execution map
    target_path = os.path.join(sandbox_dir, filename)
    logger.info(f"?? Injecting high-entropy byte streams into target sandbox path: {target_path}")

    try:
        # os.urandom generates cryptographically secure random bytes
        # These bytes have maximum data randomness, achieving near-perfect 8.0 Shannon entropy
        random_payload = os.urandom(size_kb * 1024)
        
        with open(target_path, "wb") as f:
            f.write(random_payload)
            
        logger.success(f"? Payload footprint written successfully! size: {size_kb} KB")
        
        # Verify calculated variance metrics using the project's native engine helper
        calculated_entropy = calculate_shannon_entropy(target_path)
        logger.info(f"?? Verified Payload Metrics | Calculated Shannon Entropy: {calculated_entropy} / 8.0")
        
        if calculated_entropy >= config.analysis.high_entropy_threshold:
            logger.warning(f"?? Success: Calculated entropy ({calculated_entropy}) exceeds threshold rule ({config.analysis.high_entropy_threshold})")
        else:
            logger.error("? Target threshold check error: Generated data variance did not cross configuration limit parameters.")
            
    except Exception as ex:
        logger.critical(f"? Failed to execute validation payload injection cycle: {ex}")

if __name__ == "__main__":
    inject_high_entropy_payload()
