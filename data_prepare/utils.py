import logging
import sys
from pathlib import Path


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Sets up a logger with a standard format."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def ensure_dir(path: Path | str) -> Path:
    """Ensures a directory exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
