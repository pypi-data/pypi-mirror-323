import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(pathname)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)

# File handler
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

file_handler = logging.FileHandler(
    log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
)
file_handler.setFormatter(detailed_formatter)
file_handler.setLevel(logging.DEBUG)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False 