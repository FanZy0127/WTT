import logging
import os


def get_logger(name: str, log_directory: str = "logs") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.debug(f"Creating/getting logger with name: {name}")
    # Clear existing handlers to avoid duplicates in testing
    if logger.hasHandlers():
        logger.handlers.clear()
        logger.debug("Cleared existing handlers")
    else:
        logger.debug("Logger has no existing handlers")

    handler = logging.StreamHandler()
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        logger.debug(f"Created log directory: {log_directory}")
    file_handler = logging.FileHandler(f"{log_directory}/app.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    logger.debug("Added StreamHandler and FileHandler to logger")

    return logger
