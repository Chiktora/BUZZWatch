import os
import platform
import psutil

def get_system_state():
    """
    Collects the current state of the system for debugging purposes.
    """
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory()._asdict(),
        "disk_usage": psutil.disk_usage('/')._asdict(),
        "environment_variables": {key: os.environ[key] for key in os.environ.keys() if key.startswith('PYTHON')}
    }

def validate_interval(interval):
    """
    Validates the interval to ensure it is within a reasonable range.
    """
    MIN_INTERVAL = 10  # Minimum allowable interval in seconds
    MAX_INTERVAL = 3600  # Maximum allowable interval in seconds
    if interval < MIN_INTERVAL or interval > MAX_INTERVAL:
        print(f"Warning: Interval {interval} is out of bounds. Setting to default of 300 seconds.")
        return 300
    return interval
