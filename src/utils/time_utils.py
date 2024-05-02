# utils/time_utils.py
import time


def get_timestamp():
    return int(time.time())


def calculate_time(timestamp):
    """Calculate time in minutes and seconds."""
    minutes = timestamp // 60
    seconds = timestamp % 60
    return minutes, seconds
