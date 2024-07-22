import logging
import os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        log_directory = "logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        file_handler = logging.FileHandler(f"{log_directory}/app.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    return logger
