import json
import os
import traceback
from datetime import datetime
from typing import Optional, Dict
import inspect


def _get_caller_info() -> Dict:
    """
    Retrieves information about the file name and line number of the caller.
    """
    frame = inspect.currentframe()
    caller_frame = frame.f_back.f_back
    return {
        "fileName": os.path.basename(caller_frame.f_code.co_filename),
        "lineNumber": caller_frame.f_lineno,
    }


class Logger:
    """
    Custom logging module that appends logs to a JSON file `execution_log.json`
    and provides insights like total warnings, errors, and estimated time to completion.
    """
    LOG_FILE = "execution_log.json"

    def __init__(self):
        """
        Initializes the Logger. Ensures the log file exists and sets default remaining time.
        """
        self._initialize_log_file()
        self.remaining_time = None  # Default to None unless explicitly set.

    def _initialize_log_file(self):
        """
        Creates the log file if it doesn't exist and initializes it with an empty log array.
        """
        if not os.path.exists(self.LOG_FILE):
            with open(self.LOG_FILE, "w", encoding="utf-8") as file:
                json.dump({"log": []}, file, indent=4)

    def _get_next_id(self) -> int:
        """
        Gets the next unique ID for a log entry.
        """
        with open(self.LOG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return len(data["log"]) + 1

    def _write_log(self, entry: Dict):
        """
        Appends a log entry to the JSON file.
        """
        with open(self.LOG_FILE, "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["log"].append(entry)
            file.seek(0)
            json.dump(data, file, indent=4)

    def _get_log_summary(self) -> Dict[str, int]:
        """
        Provides a summary of the log file, including the count of warnings, errors, and info logs.
        """
        with open(self.LOG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        summary = {
            "totalLogs": len(data["log"]),
            "infoCount": 0,
            "warningCount": 0,
            "errorCount": 0,
        }
        for entry in data["log"]:
            log_type = entry.get("type")
            if log_type == "info":
                summary["infoCount"] += 1
            elif log_type == "warning":
                summary["warningCount"] += 1
            elif log_type == "error":
                summary["errorCount"] += 1

        return summary

    def set_remaining_time(self, minutes: Optional[int], variable_window: Optional[int] = None):
        """
        Sets or updates the estimated remaining time for the current task.

        :param minutes: Remaining time in minutes (optional).
        :param variable_window: Additional time window in seconds for variable operations (optional).
        """
        self.remaining_time = minutes
        self.variable_window = variable_window

    def _estimate_time_remaining(self) -> str:
        """
        Estimates the remaining time for execution.
        If user-provided time is available, uses that. Otherwise, returns a default estimate.
        Includes variable time window if specified.
        """
        if self.remaining_time is not None:
            base_estimate = f"~{self.remaining_time} minutes"
            if hasattr(self, 'variable_window') and self.variable_window is not None:
                return f"{base_estimate} (±{self.variable_window} seconds for variable operations)"
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

    def log(self, log_type: str, message: str, severity: int, component: str, stack_trace: Optional[str] = None):
        """
        Adds a log entry to the log file.

        :param log_type: The type of log (info, warning, error, debug).
        :param message: A detailed message about the log entry.
        :param severity: Numeric severity of the log (1-5).
        :param component: The component generating the log entry.
        :param stack_trace: Stack trace information for error logs (optional).
        """
        in_code = _get_caller_info()
        entry = {
            "id": self._get_next_id(),
            "timestamp": int(datetime.utcnow().timestamp() * 1000),  # Unix timestamp in milliseconds
            "type": log_type,
            "message": message,
            "severity": severity,
            "component": component,
            "inCode": in_code,
        }
        if stack_trace:
            entry["stackTrace"] = stack_trace

        self._write_log(entry)
        self.display_insights()

    def info(self, message: str, component: str):
        """Logs an info message."""
        self.log("info", message, severity=2, component=component)

    def warning(self, message: str, component: str):
        """Logs a warning message."""
        self.log("warning", message, severity=3, component=component)

    def error(self, message: str, component: str, exc: Optional[Exception] = None):
        """
        Logs an error message with optional stack trace.

        :param message: A detailed error message.
        :param component: The component generating the error log.
        :param exc: Exception to include the stack trace (optional).
        """
        stack_trace = traceback.format_exc() if exc else None
        self.log("error", message, severity=4, component=component, stack_trace=stack_trace)

    def debug(self, message: str, component: str):
        """Logs a debug message."""
        self.log("debug", message, severity=1, component=component)

    def crash(self, message: str, component: str, exc: Optional[Exception] = None):
        """
        Logs a crash message with stack trace.

        :param message: A detailed crash message.
        :param component: The component generating the crash log.
        :param exc: Exception to include the stack trace (optional).
        """
        stack_trace = traceback.format_exc() if exc else None
        self.log("crash", message, severity=5, component=component, stack_trace=stack_trace)


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
