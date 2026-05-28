from datetime import datetime, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo



# NOTE: status function is intended for future API development, but is not currently used in the CLI implementation. 
# It is included here for completeness and future use.
def status(code: int, message: str, payload: Optional[Any]=None) -> dict:
    """ Creates a standardized status response.
    Args:
        code (int): Return status code
        message (str): Return status message
        payload (Optional[Any], optional): Return Payload, can be any datatype. Defaults to None.

    Returns:
        dict: Returns a dict with keys: code, message and payload.
    """
    return {"code":code,
        "message": message, 
        "payload": payload}

def status_ok(payload: Optional[Any]=None) -> dict:
    """Standard success response (code 200)."""
    return status(200, "Successful", payload)
    
def status_error(payload: Optional[Any]=None) -> dict:
    """Standard error response (code 400)."""
    return status(400, "Unsuccessful", payload)

def menu_map(options: list) -> dict: 
    
    {i + 1: item for i, item in enumerate(options)}
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
