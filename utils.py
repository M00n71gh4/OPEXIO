from typing import Any, Optional

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
    group_map = {}
    i = 0
    for item in options:
        i += 1
        group_map[i] = {"id":str(item["id"]) ,"groupName": str(item["groupName"])}
    return group_map