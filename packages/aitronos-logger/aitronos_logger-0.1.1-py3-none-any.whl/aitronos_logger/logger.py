import json
import os
import traceback
from datetime import datetime, UTC
from typing import Optional, Dict, List
import inspect
import fcntl
import errno
import tempfile
import shutil
import time
import uuid


def _get_caller_info() -> Dict:
    """
    Retrieves information about the file name, line number, and component name of the caller.
    """
    frame = inspect.currentframe()
    # We need to go up 3 frames: current -> _get_caller_info -> log -> actual caller
    caller_frame = frame.f_back.f_back.f_back
    
    # Get the component name from the caller's class or module
    try:
        if 'self' in caller_frame.f_locals:
            # If called from a class method, use the class name
            component = caller_frame.f_locals['self'].__class__.__name__
        else:
            # Otherwise use the module name (filename without extension)
            component = os.path.splitext(os.path.basename(caller_frame.f_code.co_filename))[0]
    except:
        component = "Logger"  # Fallback component name
    
    return {
        "file_name": os.path.basename(caller_frame.f_code.co_filename),
        "line_number": caller_frame.f_lineno,
        "component": component
    }


class Logger:
    """
    Custom logging module that creates and manages automation logs in JSON format.
    """
    LOG_FILE = "execution_log.json"
    LOCK_FILE = "execution_log.lock"

    def __init__(self, automation_execution_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Initializes the Logger with a new automation execution.
        
        :param automation_execution_id: Optional ID for the automation execution. If not provided, generates a UUID.
        :param metadata: Optional metadata dictionary with up to 16 key-value pairs.
        """
        self.automation_execution_id = automation_execution_id or str(uuid.uuid4())
        self.start_time = int(time.time())
        self.metadata = metadata if metadata else {}
        self._initialize_log_file()
        self.progress_percentage = 0
        self.remaining_time_seconds = None

    def _acquire_lock(self, exclusive=True):
        """Acquire a lock for file operations."""
        os.makedirs(os.path.dirname(self.LOCK_FILE) if os.path.dirname(self.LOCK_FILE) else '.', exist_ok=True)
        lock_file = open(self.LOCK_FILE, 'w+')
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        except:
            lock_file.close()
            raise
        return lock_file

    def _release_lock(self, lock_file):
        """Release the lock."""
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()

    def _initialize_log_file(self):
        """
        Creates the log file if it doesn't exist and initializes it with the automation log structure.
        """
        lock = self._acquire_lock(exclusive=True)
        try:
            initial_data = {
                "id": str(uuid.uuid4()),
                "automation_execution_id": self.automation_execution_id,
                "entries": [],
                "metadata": self.metadata
            }
            
            if not os.path.exists(self.LOG_FILE):
                with open(self.LOG_FILE, "w", encoding="utf-8") as file:
                    json.dump(initial_data, file, indent=4)
            else:
                # If file exists, read it to check if it's a new automation
                with open(self.LOG_FILE, "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                        # Check if it's a new automation or if the file structure is invalid
                        if not isinstance(data, dict) or "automation_execution_id" not in data or \
                           data["automation_execution_id"] != self.automation_execution_id:
                            # New automation or invalid structure, overwrite file
                            with open(self.LOG_FILE, "w", encoding="utf-8") as write_file:
                                json.dump(initial_data, write_file, indent=4)
                    except json.JSONDecodeError:
                        # Invalid JSON, overwrite file
                        with open(self.LOG_FILE, "w", encoding="utf-8") as write_file:
                            json.dump(initial_data, write_file, indent=4)
        finally:
            self._release_lock(lock)

    def _read_log_data(self) -> Dict:
        """Read the current log data with proper locking."""
        lock = self._acquire_lock(exclusive=True)
        try:
            with open(self.LOG_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        finally:
            self._release_lock(lock)

    def _write_log_data(self, data: Dict):
        """Write log data with proper locking."""
        lock = self._acquire_lock(exclusive=True)
        try:
            with open(self.LOG_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        finally:
            self._release_lock(lock)

    def set_progress(self, percentage: int, remaining_time_seconds: Optional[int] = None):
        """
        Sets the current progress of the automation.
        
        :param percentage: Progress percentage (0-100)
        :param remaining_time_seconds: Optional estimate of remaining time in seconds
        """
        self.progress_percentage = max(0, min(100, percentage))
        self.remaining_time_seconds = remaining_time_seconds

    def _get_progress_info(self) -> Dict:
        """Gets the current progress information."""
        current_time = int(time.time())
        return {
            "elapsed_time_seconds": current_time - self.start_time,
            "progress_percentage": self.progress_percentage,
            "remaining_time_seconds": self.remaining_time_seconds if self.remaining_time_seconds is not None else 0
        }

    def log(self, log_type: str, message: str, severity: int = 0, component: Optional[str] = None, 
            metadata: Optional[Dict] = None, stack_trace: Optional[Dict] = None):
        """
        Adds a log entry to the log file.

        :param log_type: The type of log (info, alert, error)
        :param message: A detailed message about the log entry
        :param severity: Numeric severity of the log (recommended 0-5)
        :param component: The component generating the log entry (optional)
        :param metadata: Optional metadata dictionary
        :param stack_trace: Optional stack trace information
        """
        caller_info = _get_caller_info()
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "progress": self._get_progress_info(),
            "type": log_type,
            "message": message,
            "component": component if component is not None else caller_info["component"],
            "severity": severity
        }

        if stack_trace or caller_info:
            entry["stack_trace"] = stack_trace or {
                "file_name": caller_info["file_name"],
                "line_number": caller_info["line_number"]
            }

        if metadata:
            entry["metadata"] = {k: str(v)[:512] for k, v in list(metadata.items())[:16]}

        data = self._read_log_data()
        data["entries"].append(entry)
        self._write_log_data(data)

    def info(self, message: str, component: Optional[str] = None, metadata: Optional[Dict] = None):
        """Logs an info message."""
        self.log("info", message, severity=0, component=component, metadata=metadata)

    def alert(self, message: str, component: Optional[str] = None, metadata: Optional[Dict] = None):
        """Logs an alert message."""
        self.log("alert", message, severity=2, component=component, metadata=metadata)

    def error(self, message: str, component: Optional[str] = None, exc: Optional[Exception] = None, 
             metadata: Optional[Dict] = None):
        """
        Logs an error message with stack trace.

        :param message: A detailed error message
        :param component: The component generating the error log (optional)
        :param exc: Exception to include the stack trace (optional)
        :param metadata: Optional metadata dictionary
        """
        stack_trace = None
        if exc:
            tb = traceback.extract_tb(exc.__traceback__)[-1]
            stack_trace = {
                "file_name": os.path.basename(tb.filename),
                "line_number": tb.lineno
            }
        self.log("error", message, severity=4, component=component, stack_trace=stack_trace, metadata=metadata)

    def _get_log_summary(self) -> Dict[str, int]:
        """
        Provides a summary of the log file, including the count of warnings, errors, and info logs.
        """
        self._initialize_log_file()
        data = self._read_log_data()

        summary = {
            "totalLogs": len(data["entries"]),
            "infoCount": 0,
            "warningCount": 0,
            "errorCount": 0,
        }
        for entry in data["entries"]:
            log_type = entry.get("type")
            if log_type == "info":
                summary["infoCount"] += 1
            elif log_type == "warning":
                summary["warningCount"] += 1
            elif log_type == "error":
                summary["errorCount"] += 1

        return summary

    def _get_next_id(self) -> int:
        """
        Gets the next unique ID for a log entry.
        """
        self._initialize_log_file()
        data = self._read_log_data()
        return len(data["entries"]) + 1

    def _estimate_time_remaining(self) -> str:
        """
        Estimates the remaining time for execution.
        If user-provided time is available, uses that. Otherwise, returns a default estimate.
        Includes variable time window if specified.
        """
        if self.remaining_time_seconds is not None:
            base_estimate = f"~{self.remaining_time_seconds} seconds"
            return f"{base_estimate} remaining"
        return "Time remaining: unknown"

    def display_insights(self):
        """
        Displays a summary of the log file and estimated time to completion.
        """
        summary = self._get_log_summary()
        time_remaining = self._estimate_time_remaining()

        print("---- Log Insights ----")
        print(f"Total Logs: {summary['totalLogs']}")
        print(f"Info Logs: {summary['infoCount']}")
        print(f"Warnings: {summary['warningCount']}")
        print(f"Errors: {summary['errorCount']}")
        print(f"Estimated Time Remaining: {time_remaining}")
        print("-----------------------")


# Example Usage
# if __name__ == "__main__":
#     logger = Logger()
#     logger.info("Automation execution started", component="MainExecutor")
#
#     # Set remaining time
#     logger.set_remaining_time(10)  # User sets remaining time as 10 minutes.
#
#     try:
#         # Simulate an error
#         1 / 0
#     except Exception as e:
#         logger.error("Failed to execute division operation", component="MathModule", exc=e)
#
#     logger.warning("Potential configuration issue detected", component="ConfigValidator")
#     logger.debug("Debugging execution details", component="MainExecutor")
