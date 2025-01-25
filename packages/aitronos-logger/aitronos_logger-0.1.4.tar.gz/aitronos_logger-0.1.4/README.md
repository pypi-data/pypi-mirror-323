# Aitronos Logger

A sophisticated logging module that provides JSON-based logging with insights and time estimation capabilities. The logger stores all logs in a structured JSON format, making it easy to analyze and process log data programmatically.

## Features

- JSON-based logging with structured data
- Automatic progress tracking across all log types
- Smart stack trace detection
- Multiple log types (info, alert, error)
- Automatic component detection from caller
- Customizable severity levels (0-5)
- Thread-safe file operations
- Support for metadata in logs

## Installation

```bash
pip install aitronos-logger
```

## Usage

### Basic Usage

```python
from aitronos_logger import Logger

# Initialize the logger (all parameters optional)
logger = Logger(
    automation_execution_id="my-execution-123",
    metadata={"environment": "production"}
)

# Set initial progress (automatically tracked in all subsequent logs)
logger.set_progress(remaining_time_seconds=300)  # 5 minutes remaining

# Basic logging with automatic progress tracking
logger.info("Application started", severity=1)
logger.alert("Important notification", severity=3)
logger.error("Operation failed")  # Severity defaults to 4 for errors

# Progress is automatically tracked and updated
logger.info("Processing data", severity=2)  # Uses last known progress

# Errors automatically capture stack traces
try:
    result = 1 / 0
except Exception as e:
    # Stack trace and error details are automatically captured
    logger.error("Division error occurred")

# Add custom metadata to any log
logger.info(
    "User action completed",
    severity=1,
    metadata={"user_id": "123", "action": "login"}
)
```

### Progress Tracking

The logger automatically tracks progress across all log entries. You only need to update the progress when it changes:

```python
# Update progress - automatically included in all subsequent logs
logger.set_progress(remaining_time_seconds=180)  # 3 minutes remaining

# These logs will include the updated progress
logger.info("Step 1 completed", severity=1)
logger.alert("Approaching deadline", severity=3)

# Progress is calculated based on elapsed and remaining time
logger.set_progress(remaining_time_seconds=60)  # 1 minute remaining
logger.info("Final step", severity=1)
```

### Log File Structure

The logger creates a JSON file (`execution_log.json`) with structured log entries:

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "automation_execution_id": "my-execution-123",
    "entries": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "timestamp": 1706062800000,
            "progress": {
                "elapsed_time_seconds": 120,
                "progress_percentage": 40,  // Automatically calculated
                "remaining_time_seconds": 180
            },
            "type": "info",
            "message": "Step 1 completed",
            "component": "MainApp",  // Automatically detected
            "severity": 1,
            "stack_trace": {
                "file_name": "main.py",
                "line_number": 10
            }
        }
    ],
    "metadata": {
        "environment": "production"
    }
}
```

### Log Types and Severity

Each log type supports severity levels (0-5) for fine-grained control:

- `info(message, severity=1)`: General information (default severity 1)
- `alert(message, severity=3)`: Important notifications (default severity 3)
- `error(message, severity=4)`: Error messages (default severity 4)

Common parameters for all log methods:
- `message`: The log message
- `severity`: Optional severity level (0-5)
- `component`: Optional component name (auto-detected if not provided)
- `metadata`: Optional dictionary of additional data

Features automatically handled by the logger:
- Progress tracking and percentage calculation
- Stack trace capture for errors
- Component detection from caller
- Timestamp and log ID generation
- File locking for thread safety

### Insights and Monitoring

Get real-time insights into your logging:

```python
logger.display_insights()
```

Output:
```
---- Log Insights ----
Total Logs: 5
Info Logs: 3
Alerts: 1
Errors: 1
Estimated Time Remaining: ~180 seconds remaining
-----------------------
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Version Management

The project includes a version management script that handles version bumping, package building, and publishing:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/update_version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/update_version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/update_version.py major

# Test upload to TestPyPI
python scripts/update_version.py patch --test

# Skip git operations
python scripts/update_version.py patch --no-git
```

The script will:
1. Bump the version in `pyproject.toml`
2. Clean build directories
3. Build the package (sdist and wheel)
4. Commit changes and create a git tag
5. Upload to PyPI (or TestPyPI with `--test`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
