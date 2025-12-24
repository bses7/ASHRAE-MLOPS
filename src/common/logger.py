import logging
import sys
from pathlib import Path

def get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Returns a standardized logger that outputs to both console and file.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(log_level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "pipeline_execution.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger