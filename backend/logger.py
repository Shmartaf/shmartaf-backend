import json


def log_decorator(func):
    """Decorator to conditionally log function details based on the log level and handle exceptions."""

    def wrapper(*args, **kwargs):
        try:
            if ColorLogger.CURRENT_LEVEL == "DEBUG":
                # Detailed logging for DEBUG level
                kwargs_str = ", ".join([f"{key}={value}" for key, value in kwargs.items()])
                args_str = ", ".join([repr(a) for a in args])
                ColorLogger.log(
                    f"Calling {func.__name__} with args: [{args_str}] and kwargs: {{{kwargs_str}}}",
                    "DEBUG",
                )
                result = func(*args, **kwargs)
                ColorLogger.log(f"{func.__name__} returned {result}", "DEBUG")
            else:
                # Simplified logging for other levels
                result = func(*args, **kwargs)
                ColorLogger.log(f"{func.__name__} executed successfully.", "INFO")

            return result
        except Exception as e:
            ColorLogger.log(f"Error in {func.__name__}: {e}", "ERROR")
            raise  # Re-throw the exception after logging

    return wrapper


class ColorLogger:
    """A simple logger that prints colored messages based on the log level, with support for logging structured data."""

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }
    CURRENT_LEVEL = "INFO"  # Default log level

    @staticmethod
    def set_level(level):
        """Set the current logging level."""
        ColorLogger.CURRENT_LEVEL = level.upper()

    @staticmethod
    def log(message, level="INFO", data=None):
        """Log a message with the specified level and optional structured data."""
        if ColorLogger.COLORS.get(level, "INFO") >= ColorLogger.COLORS.get(ColorLogger.CURRENT_LEVEL, "INFO"):
            color = ColorLogger.COLORS.get(level, "\033[92m")  # Default to green if level not found
            reset = "\033[0m"  # Reset color

            data_str = ""
            if data is not None:
                # Convert dict or JSON string to a pretty-printed string
                if isinstance(data, str):
                    try:
                        data = json.loads(data)  # Try to parse string as JSON
                    except json.JSONDecodeError:
                        data_str = " (Invalid JSON)"
                if isinstance(data, dict):
                    data_str = " " + json.dumps(data, indent=2)

            print(f"{color}[{level}]: {message}{data_str}{reset}")
