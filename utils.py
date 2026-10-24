from datetime import datetime, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo


def menu_map(options: list) -> dict: 
    
    group_map = {}
    i = 0
    for item in options:
        i += 1
        group_map[i] = item
    return group_map


def local_time_now(lokal_timezone: ZoneInfo) -> datetime:
    """Returns the current local time as a timezone-aware datetime object."""
    return datetime.now(timezone.utc).astimezone(lokal_timezone)

def check_datetime(user_input: str, date_time_format_computer: str, date_time_format_human: str, time_zone: ZoneInfo) -> datetime:
    """Checks if the user input is a valid date and time in the format.
        Intended to standarize date/time format across the application.
    Args:
        user_input (str): str in the input format, for example '%d-%m-%Y %H:%M' for 'DD-MM-YYYY HH:MM'
    Raises:
        ValueError: If the user input is not in the correct format, a ValueError is raised with an appropriate error message.
    Returns:
        datetime: Returns a datetime object if the user input is in the correct format.
    """
    try:
        date_time = datetime.strptime(user_input, date_time_format_computer)# This will raise a ValueError if the format is incorrect
        date_time = date_time.replace(tzinfo=time_zone)
        return date_time 
    except ValueError as e:
        raise ValueError(f"Invalid date format. Please enter the date and time in the format '{date_time_format_human}'.") from e
