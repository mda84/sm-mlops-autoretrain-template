import logging
import os
from typing import Optional


def configure_logging(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '{"level":"%(levelname)s","time":"%(asctime)s","name":"%(name)s","message":"%(message)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        logger.setLevel(getattr(logging, env_level.upper(), level))
    return logger
