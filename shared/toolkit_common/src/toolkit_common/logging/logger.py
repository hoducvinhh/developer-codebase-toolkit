"""Standard logging helpers for CLI tools."""

import logging
import sys
from typing import Any, Optional


def setup_logger(
    name: str = "toolkit",
    verbose: bool = False,
    quiet: bool = False,
    stream: Optional[Any] = None,
) -> logging.Logger:
    """Configure and return a standard logger."""
    logger = logging.getLogger(name)
    logger.handlers.clear()

    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setLevel(level)

    fmt = "[%(levelname)s] %(message)s" if not verbose else "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
