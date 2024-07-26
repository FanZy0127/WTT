import logging
import os
import pytest
from app.logger import get_logger

@pytest.fixture
def test_log_directory():
    log_directory = "test_logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    yield log_directory
    # Clean up the directory after the test
    if os.path.exists(log_directory):
        for file in os.listdir(log_directory):
            file_path = os.path.join(log_directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(log_directory)

def test_get_logger(test_log_directory):
    logger_name = "test_logger"
    logger = get_logger(logger_name, log_directory=test_log_directory)

    print(f"Logger name: {logger.name}")
    print(f"Logger level: {logger.level}")
    assert logger.name == logger_name
    assert logger.level == logging.INFO

    handlers = logger.handlers
    print(f"Handlers: {handlers}")
    assert len(handlers) == 2, f"Expected 2 handlers, found {len(handlers)}"

    stream_handler = next((h for h in handlers if isinstance(h, logging.StreamHandler)), None)
    file_handler = next((h for h in handlers if isinstance(h, logging.FileHandler)), None)

    assert stream_handler is not None, "StreamHandler not found"
    assert file_handler is not None, "FileHandler not found"

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    assert stream_handler.formatter._fmt == formatter._fmt, "StreamHandler formatter mismatch"
    assert file_handler.formatter._fmt == formatter._fmt, "FileHandler formatter mismatch"

    logger.info("Test info message")
    logger.error("Test error message")

    log_file_path = os.path.join(test_log_directory, "app.log")
    assert os.path.exists(log_file_path), "Log file not created"

    with open(log_file_path, "r", encoding="utf-8") as log_file:
        log_content = log_file.read()
        assert "Test info message" in log_content, "Info message not found in log file"
        assert "Test error message" in log_content, "Error message not found in log file"

    # Clean up handlers
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()

    # Ensure all handlers are closed and then delete the directory
    logging.shutdown()
    if os.path.exists(test_log_directory):
        for file in os.listdir(test_log_directory):
            file_path = os.path.join(test_log_directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(test_log_directory)
