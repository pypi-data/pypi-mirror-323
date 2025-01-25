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
import queue
import threading
from pathlib import Path


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
    Custom logging module that creates and manages automation logs in JSON format using a queue.
    """
    LOG_FILE = "execution_log.json"
    
    def __init__(self, automation_execution_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Initializes the Logger with a new automation execution and starts the log processing thread.
        
        :param automation_execution_id: Optional ID for the automation execution. If not provided, generates a UUID.
        :param metadata: Optional metadata dictionary with up to 16 key-value pairs.
        """
        self.automation_execution_id = automation_execution_id or str(uuid.uuid4())
        self.start_time = int(time.time())
        self.metadata = metadata if metadata else {}
        self.progress_percentage = 0
        self.remaining_time_seconds = None
        
        # Initialize the log queue and processing thread
        self.log_queue = queue.Queue()
        self.should_stop = False
        self.log_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.log_thread.start()
        
        # Ensure log directory exists
        log_path = Path(self.LOG_FILE)
        if log_path.parent != Path('.'):
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.LOG_FILE):
            self._initialize_log_file()
            
        # Add initial log entry
        self._queue_log_entry({
            "id": str(uuid.uuid4()),
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "type": "info",
            "message": "Logger initialized",
            "component": "Logger",
            "severity": 1,
            "progress": {
                "elapsed_time_seconds": 0,
                "progress_percentage": 0,
                "remaining_time_seconds": 0,
                "status": "Initialized"
            },
            "stack_trace": self._get_stack_trace(1)
        })

    def __del__(self):
        """Ensure the queue is processed before the logger is destroyed."""
        self.should_stop = True
        if hasattr(self, 'log_thread') and self.log_thread.is_alive():
            self.log_queue.put(None)  # Signal to stop processing
            self.log_thread.join(timeout=5.0)  # Wait up to 5 seconds for queue to process

    def _process_log_queue(self):
        """Process log entries from the queue and write them to the file."""
        while not self.should_stop:
            try:
                entry = self.log_queue.get(timeout=1.0)
                if entry is None:  # Stop signal
                    break
                
                try:
                    # Read current log data
                    if os.path.exists(self.LOG_FILE):
                        with open(self.LOG_FILE, 'r', encoding='utf-8') as f:
                            try:
                                data = json.load(f)
                            except json.JSONDecodeError:
                                data = self._create_initial_data()
                    else:
                        data = self._create_initial_data()
                    
                    # Append new entry
                    data["entries"].append(entry)
                    
                    # Write updated data back to file
                    with open(self.LOG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                        
                except Exception as e:
                    print(f"Error processing log entry: {str(e)}")
                
                finally:
                    self.log_queue.task_done()
                    
            except queue.Empty:
                continue  # Keep checking for new entries
            except Exception as e:
                print(f"Error in log processing thread: {str(e)}")
                time.sleep(1)  # Prevent tight loop in case of persistent errors

    def _queue_log_entry(self, entry: Dict):
        """Add a log entry to the processing queue."""
        self.log_queue.put(entry)

    def _initialize_log_file(self):
        """Creates or reinitializes the log file."""
        initial_data = self._create_initial_data()
        with open(self.LOG_FILE, "w", encoding="utf-8") as file:
            json.dump(initial_data, file, indent=4)

    def _create_initial_data(self) -> Dict:
        """Creates initial log data structure."""
        return {
            "id": str(uuid.uuid4()),
            "automation_execution_id": self.automation_execution_id,
            "entries": [],
            "metadata": self.metadata
        }

    def _read_log_data(self) -> Dict:
        """Read the current log data."""
        if not os.path.exists(self.LOG_FILE):
            return self._create_initial_data()
        
        try:
            with open(self.LOG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if data.get("automation_execution_id") != self.automation_execution_id:
                    return self._create_initial_data()
                return data
        except (json.JSONDecodeError, KeyError):
            return self._create_initial_data()

    def _get_log_summary(self) -> Dict[str, int]:
        """
        Provides a summary of the log file, including the count of warnings, errors, and info logs.
        """
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
        data = self._read_log_data()
        return len(data["entries"]) + 1

    def set_progress(self, remaining_time_seconds: Optional[int] = None):
        """
        Sets the current progress of the automation by automatically calculating the percentage
        based on elapsed time and remaining time.
        
        :param remaining_time_seconds: Estimate of remaining time in seconds. If None, progress
                                     will be calculated based on elapsed time only.
        """
        elapsed_time = int(time.time()) - self.start_time
        
        if remaining_time_seconds is not None:
            total_time = elapsed_time + remaining_time_seconds
            self.progress_percentage = min(100, int((elapsed_time / total_time) * 100)) if total_time > 0 else 0
            self.remaining_time_seconds = remaining_time_seconds
        else:
            # When no remaining time is provided, use elapsed time to estimate progress
            # Assuming longer elapsed time indicates more progress
            # Using a logarithmic scale to prevent rapid progress at the start
            # and slower progress over time
            self.progress_percentage = min(100, int(100 * (1 - 1 / (1 + elapsed_time / 3600))))
            self.remaining_time_seconds = None

    def _get_progress_info(self) -> Dict:
        """Gets the current progress information."""
        current_time = int(time.time())
        return {
            "elapsed_time_seconds": current_time - self.start_time,
            "progress_percentage": self.progress_percentage,
            "remaining_time_seconds": self.remaining_time_seconds if self.remaining_time_seconds is not None else 0
        }

    def _get_stack_trace(self, depth: int = 1) -> Dict:
        """
        Automatically retrieves stack trace information from the caller.
        """
        frame = inspect.currentframe()
        for _ in range(depth + 1):  # +1 to skip this method
            if frame.f_back is None:
                break
            frame = frame.f_back
            
        if frame:
            return {
                "file_name": os.path.basename(frame.f_code.co_filename),
                "line_number": frame.f_lineno,
                "function_name": frame.f_code.co_name
            }
        return {}

    def _validate_progress_data(self, progress: Optional[Dict | int | float] = None) -> Dict:
        """Validates and formats progress data."""
        progress_info = {
            "elapsed_time_seconds": int(time.time()) - self.start_time,
            "progress_percentage": 0,
            "remaining_time_seconds": 0
        }
        
        if progress is not None:
            if isinstance(progress, dict):
                progress_info["remaining_time_seconds"] = progress.get('remaining_time_seconds', 0)
                if 'progress_percentage' in progress:
                    progress_info["progress_percentage"] = min(100, max(0, int(progress['progress_percentage'])))
            elif isinstance(progress, (int, float)):
                progress_info["progress_percentage"] = min(100, max(0, int(progress)))
        else:
            progress_info["status"] = "No progress information available"
            
        return progress_info

    def log(self, log_type: str, message: str, severity: int = 0, component: Optional[str] = None,
            metadata: Optional[Dict] = None, progress: Optional[Dict] = None):
        """
        Adds a log entry to the log file.

        :param log_type: The type of log (info, alert, error)
        :param message: A detailed message about the log entry
        :param severity: Numeric severity of the log (0-5, where 0 is lowest and 5 is highest)
        :param component: The component generating the log entry (optional, auto-detected if not provided)
        :param metadata: Optional metadata dictionary
        :param progress: Optional progress information as dict with keys:
                        - remaining_time_seconds: estimated remaining time
                        - progress_percentage: current progress (0-100)
        """
        caller_info = _get_caller_info()
        stack_trace = self._get_stack_trace(2)
        progress_info = self._validate_progress_data(progress)
        
        # Ensure severity is between 0 and 5
        severity = min(5, max(0, severity))
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
            "progress": progress_info,
            "type": log_type,
            "message": message,
            "component": component if component is not None else caller_info["component"],
            "severity": severity,
            "stack_trace": stack_trace
        }

        if metadata:
            entry["metadata"] = {k: str(v)[:512] for k, v in list(metadata.items())[:16]}

        self._queue_log_entry(entry)

    def info(self, message: str, severity: int = 1, component: Optional[str] = None,
             metadata: Optional[Dict] = None, progress: Optional[Dict] = None):
        """
        Logs an info message.
        
        :param message: The info message to log
        :param severity: Severity level (0-5), defaults to 1 for info
        :param component: Optional component name (auto-detected if not provided)
        :param metadata: Optional metadata dictionary
        :param progress: Optional progress information
        """
        self.log("info", message, severity=severity, component=component,
                metadata=metadata, progress=progress)

    def alert(self, message: str, severity: int = 3, component: Optional[str] = None,
              metadata: Optional[Dict] = None, progress: Optional[Dict] = None):
        """
        Logs an alert message.
        
        :param message: The alert message to log
        :param severity: Severity level (0-5), defaults to 3 for alerts
        :param component: Optional component name (auto-detected if not provided)
        :param metadata: Optional metadata dictionary
        :param progress: Optional progress information
        """
        self.log("alert", message, severity=severity, component=component,
                metadata=metadata, progress=progress)

    def error(self, message: str, severity: int = 5, component: Optional[str] = None,
              metadata: Optional[Dict] = None, progress: Optional[Dict] = None, exc: Optional[Exception] = None):
        """
        Logs an error message with automatic stack trace detection.
        
        :param message: The error message to log
        :param severity: Severity level (0-5), defaults to 5 for errors
        :param component: Optional component name (auto-detected if not provided)
        :param metadata: Optional metadata dictionary
        :param progress: Optional progress information
        :param exc: Optional exception object for enhanced stack trace information
        """
        if exc:
            if metadata is None:
                metadata = {}
            metadata['exception_type'] = exc.__class__.__name__
            metadata['exception_message'] = str(exc)
            
        self.log("error", message, severity=severity, component=component,
                metadata=metadata, progress=progress)

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
#     # Set progress with remaining time
#     logger.set_progress(remaining_time_seconds=600)  # Set 10 minutes remaining
#
#     try:
#         # Simulate an error
#         1 / 0
#     except Exception as e:
#         logger.error("Failed to execute division operation", component="MathModule", exc=e)
#
#     # Log an alert for a potential issue
#     logger.alert("Potential configuration issue detected", component="ConfigValidator")
#     
#     # Log another info message
#     logger.info("Processing completed", component="MainExecutor")
