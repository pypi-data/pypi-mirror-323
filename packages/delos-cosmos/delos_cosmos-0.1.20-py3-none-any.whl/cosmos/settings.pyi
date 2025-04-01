from enum import Enum

from loguru import logger as logger

class VerboseLevel(int, Enum):
    SILENT = 0
    INFO = 1
    DEBUG = 2

logger.add("app.log", format="{time} {level} {message}", level="INFO")

__all__ = ["VerboseLevel", "logger"]
