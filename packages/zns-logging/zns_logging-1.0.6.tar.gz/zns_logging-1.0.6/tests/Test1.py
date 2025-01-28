import logging

from zns_logging import get_logger

logger = get_logger(__name__, level="NOTSETT")
# logger = get_logger(__name__, level=[])

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
