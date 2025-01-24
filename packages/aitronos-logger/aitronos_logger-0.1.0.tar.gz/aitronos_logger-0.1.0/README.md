# Aitronos Logger

A sophisticated logging module that provides JSON-based logging with insights and time estimation capabilities. The logger stores all logs in a structured JSON format, making it easy to analyze and process log data programmatically.

## Features

- JSON-based logging with structured data
- Log insights and statistics with real-time display
- Time estimation for operations with variable window support
- Multiple log levels (debug, info, warning, error, crash)
- Automatic stack trace capture for errors and crashes
- Caller information tracking (file name and line number)
- Severity levels (1-5) for fine-grained log importance

## Installation

```bash
pip install aitronos-logger
```

## Usage

### Basic Usage

```python
from aitronos_logger import Logger

# Initialize the logger
logger = Logger()

# Log different types of messages
logger.info("Application started", component="MainApp")
logger.debug("Configuration loaded", component="ConfigModule")
logger.warning("Low memory warning", component="MemoryManager")

# Log an error with exception tracking
try:
    result = 1 / 0
except Exception as e:
    logger.error("Division by zero error", component="Calculator", exc=e)
```

### Time Estimation

```python
# Set estimated time remaining (10 minutes with ±30 seconds variation)
logger.set_remaining_time(10, variable_window=30)

# Get insights including time estimation
logger.display_insights()
```

### Sample Output

The logger creates a JSON file (`execution_log.json`) with structured log entries:

```json
{
    "log": [
        {
            "id": 1,
            "timestamp": 1706062800000,
            "type": "info",
            "message": "Application started",
            "severity": 2,
            "component": "MainApp",
            "inCode": {
                "fileName": "main.py",
                "lineNumber": 10
            }
        },
        {
            "id": 2,
            "timestamp": 1706062801000,
            "type": "error",
            "message": "Division by zero error",
            "severity": 4,
            "component": "Calculator",
            "inCode": {
                "fileName": "main.py",
                "lineNumber": 15
            },
            "stackTrace": "Traceback (most recent call last):\n  File \"main.py\", line 15, in <module>\n    result = 1 / 0\nZeroDivisionError: division by zero"
        }
    ]
}
```

When `display_insights()` is called, you'll see a summary like this:

```
---- Log Insights ----
Total Logs: 2
Info Logs: 1
Warnings: 0
Errors: 1
Estimated Time Remaining: ~10 minutes (±30 seconds for variable operations)
-----------------------
```

## Log Levels and Severity

The logger supports multiple log levels with corresponding default severity:

- `debug()`: Severity 1 - Detailed information for debugging
- `info()`: Severity 2 - General information about program execution
- `warning()`: Severity 3 - Warning messages for potential issues
- `error()`: Severity 4 - Error messages with optional stack traces
- `crash()`: Severity 5 - Critical failures with automatic stack traces

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
