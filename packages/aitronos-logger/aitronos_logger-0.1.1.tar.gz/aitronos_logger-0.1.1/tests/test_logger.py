import json
import os
import pytest
import fcntl
import time
import contextlib
from aitronos_logger import Logger

def safe_remove_file(file_path):
    """Safely remove a file with retries."""
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        except (OSError, IOError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue

@contextlib.contextmanager
def acquire_file_lock(lock_file_path):
    """Context manager for file locking."""
    lock_file = None
    try:
        lock_file = open(lock_file_path, 'w+')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield lock_file
    finally:
        if lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()

@pytest.fixture(autouse=True)
def cleanup_files():
    """Cleanup files before and after each test."""
    # Clean up before test
    for file in [Logger.LOG_FILE, Logger.LOCK_FILE]:
        safe_remove_file(file)
    
    yield
    
    # Clean up after test
    for file in [Logger.LOG_FILE, Logger.LOCK_FILE]:
        safe_remove_file(file)

@pytest.fixture
def logger():
    """Create a logger instance for testing."""
    return Logger(automation_execution_id="test-automation-001")

def read_log_file():
    """Read the log file with proper locking."""
    with acquire_file_lock(Logger.LOCK_FILE):
        if not os.path.exists(Logger.LOG_FILE):
            return {"entries": []}
        with open(Logger.LOG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"entries": []}

def test_logger_initialization(logger):
    """Test logger initialization and file structure"""
    assert os.path.exists(Logger.LOG_FILE)
    data = read_log_file()
    assert "id" in data
    assert data["automation_execution_id"] == "test-automation-001"
    assert "entries" in data
    assert isinstance(data["entries"], list)
    assert "metadata" in data
    assert isinstance(data["metadata"], dict)

def test_info_logging_with_auto_component(logger):
    """Test info logging with automatic component detection"""
    logger.info("Test info message")
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert latest_log["type"] == "info"
    assert latest_log["message"] == "Test info message"
    assert latest_log["component"] == "test_logger"  # Auto-detected from filename
    assert latest_log["severity"] == 0
    assert "stack_trace" in latest_log
    assert "file_name" in latest_log["stack_trace"]
    assert "line_number" in latest_log["stack_trace"]

def test_info_logging_with_manual_component(logger):
    """Test info logging with manually specified component"""
    logger.info("Test info message", component="TestComponent")
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert latest_log["type"] == "info"
    assert latest_log["message"] == "Test info message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 0

def test_info_logging_with_metadata(logger):
    """Test info logging with metadata"""
    metadata = {"key1": "value1", "key2": "value2"}
    logger.info("Test info message", metadata=metadata)
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert "metadata" in latest_log
    assert latest_log["metadata"] == metadata

class TestLoggerInClass:
    def test_component_from_class(self, logger):
        """Test component auto-detection from class"""
        logger.info("Test message from class")
        time.sleep(0.1)  # Allow for file writing
        data = read_log_file()
        latest_log = data["entries"][-1]
        assert latest_log["component"] == "TestLoggerInClass"

def test_error_logging_with_auto_component(logger):
    """Test error logging with automatic component detection"""
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Test error message", exc=e)
    
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "error"
    assert latest_log["message"] == "Test error message"
    assert latest_log["component"] == "test_logger"
    assert latest_log["severity"] == 4
    assert "stack_trace" in latest_log

def test_error_logging_with_manual_component(logger):
    """Test error logging with manually specified component"""
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Test error message", component="TestComponent", exc=e)
    
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "error"
    assert latest_log["message"] == "Test error message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 4
    assert "stack_trace" in latest_log

def test_alert_logging(logger):
    """Test alert logging"""
    logger.alert("Test alert")
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "alert"
    assert latest_log["component"] == "test_logger"
    assert latest_log["severity"] == 2

@pytest.mark.slow
def test_progress_tracking(logger):
    """Test progress tracking functionality"""
    # Set initial progress
    logger.set_progress(25, remaining_time_seconds=300)
    logger.info("Progress check 1")
    time.sleep(0.1)  # Allow for file writing
    
    # Wait a bit and set new progress
    time.sleep(1)
    logger.set_progress(50, remaining_time_seconds=200)
    logger.info("Progress check 2")
    time.sleep(0.1)  # Allow for file writing
    
    data = read_log_file()
    first_log = data["entries"][-2]
    second_log = data["entries"][-1]
    
    # Check first log
    assert first_log["progress"]["progress_percentage"] == 25
    assert first_log["progress"]["remaining_time_seconds"] == 300
    assert first_log["progress"]["elapsed_time_seconds"] >= 0
    
    # Check second log
    assert second_log["progress"]["progress_percentage"] == 50
    assert second_log["progress"]["remaining_time_seconds"] == 200
    assert second_log["progress"]["elapsed_time_seconds"] >= 1

def test_metadata_limits(logger):
    """Test metadata size limits"""
    # Create metadata with more than 16 keys and values longer than 512 chars
    large_metadata = {
        f"key_{i}": "x" * 600 for i in range(20)
    }
    
    logger.info("Test metadata limits", metadata=large_metadata)
    time.sleep(0.1)  # Allow for file writing
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert len(latest_log["metadata"]) <= 16  # Should be limited to 16 keys
    for value in latest_log["metadata"].values():
        assert len(value) <= 512  # Values should be truncated to 512 chars

def test_multiple_automations(logger):
    """Test handling of multiple automation executions"""
    # Create first log
    logger.info("First automation log")
    time.sleep(0.1)  # Allow for file writing
    first_data = read_log_file()
    first_id = first_data["automation_execution_id"]
    
    # Create new logger with different automation ID
    new_logger = Logger(automation_execution_id="test-automation-002")
    new_logger.info("Second automation log")
    time.sleep(0.1)  # Allow for file writing
    second_data = read_log_file()
    
    assert second_data["automation_execution_id"] == "test-automation-002"
    assert second_data["automation_execution_id"] != first_id
    assert len(second_data["entries"]) == 1  # Should only have the new log 