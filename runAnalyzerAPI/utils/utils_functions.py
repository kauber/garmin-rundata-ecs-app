import numpy as np
import pandas as pd


def list_element_to_int(my_list: list):
    """
    returns elements of a list as integers
    """
    try:
        res = [int(x) for x in my_list]
        if len(res) > 2:
            return res[0] * 3600 + res[1] * 60 + res[2]
        else:
            return res[0] * 60 + res[1]
    except Exception as e:
        return np.nan


def hms_to_secs(time: pd.Series):
    """
    Converts time in the h:m:s format to seconds using the list_element_to_int fun
    """
    temp = time.apply(lambda x: x.split('.')[0])  # remove decimals (all after .)
    temp2 = temp.str.split(':')
    return temp2.apply(lambda x: list_element_to_int(x))


def secs_to_hms(seconds):
    """
    Converts a time duration in seconds to HH:MM:SS.ss format.

    Args:
        seconds (float): Time in seconds.

    Returns:
        str: Time formatted as HH:MM:SS.ss.
    """
    if seconds < 0:
        raise ValueError("Seconds cannot be negative")

    # Extract hours, minutes, and seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60

    # Format the time string
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{remaining_seconds:05.2f}"  # HH:MM:SS.ss
    else:
        return f"{minutes:02}:{remaining_seconds:05.2f}"  # MM:SS.ss


def clean_nan_values(data):
    """
    Recursively replace NaN and invalid float values in nested structures (dicts/lists).

    Args:
        data: The data to clean (can be dict, list, or scalar).

    Returns:
        Cleaned data with NaN and invalid values replaced.
    """
    if isinstance(data, dict):
        return {k: clean_nan_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(v) for v in data]
    elif isinstance(data, float):
        # Replace NaNs and infinities with 0 (or another default value)
        if data != data or data in [float("inf"), float("-inf")]:
            return 0
    return data

