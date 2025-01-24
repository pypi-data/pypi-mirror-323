import json
import os
import pytest
from aitronos_logger import Logger

@pytest.fixture
def logger():
    yield Logger()
    # Cleanup after tests
    if os.path.exists(Logger.LOG_FILE):
        os.remove(Logger.LOG_FILE)

def read_log_file():
    with open(Logger.LOG_FILE, 'r') as f:
        return json.load(f)

def test_logger_initialization(logger):
    assert os.path.exists(Logger.LOG_FILE)
    data = read_log_file()
    assert "log" in data
    assert isinstance(data["log"], list)

def test_info_logging(logger):
    logger.info("Test info message", "TestComponent")
    data = read_log_file()
    latest_log = data["log"][-1]
    assert latest_log["type"] == "info"
    assert latest_log["message"] == "Test info message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 2

def test_error_logging(logger):
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Test error message", "TestComponent", exc=e)
    
    data = read_log_file()
    latest_log = data["log"][-1]
    assert latest_log["type"] == "error"
    assert latest_log["message"] == "Test error message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 4
    assert "stackTrace" in latest_log

def test_time_estimation(logger):
    logger.set_remaining_time(10, 30)
    estimate = logger._estimate_time_remaining()
    assert "~10 minutes" in estimate
    assert "±30 seconds" in estimate 