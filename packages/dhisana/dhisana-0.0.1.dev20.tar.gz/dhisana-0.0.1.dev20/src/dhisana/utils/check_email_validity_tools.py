import os
from typing import Dict, List, Optional
import aiohttp

# Decorator for demonstration purposes; 
# in your codebase this might do logging, handle exceptions, etc.
def assistant_tool(func):
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------------
# 1. Access Token Helpers
# --------------------------------------------------------------------------------

def get_zero_bounce_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the ZeroBounce access token from the provided tool configuration or environment.

    Raises:
        ValueError: If the token is not found.
    """
    if tool_config:
        zerobounce_config = next(
            (item for item in tool_config if item.get("name") == "zerobounce"), None
        )
        if zerobounce_config:
            config_map = {
                c["name"]: c["value"]
                for c in zerobounce_config.get("configuration", [])
                if c
            }
            ZERO_BOUNCE_API_KEY = config_map.get("apiKey")
        else:
            ZERO_BOUNCE_API_KEY = None
    else:
        ZERO_BOUNCE_API_KEY = None

    ZERO_BOUNCE_API_KEY = ZERO_BOUNCE_API_KEY or os.getenv("ZERO_BOUNCE_API_KEY")
    if not ZERO_BOUNCE_API_KEY:
        raise ValueError("ZERO_BOUNCE_API_KEY not found in config or env.")
    return ZERO_BOUNCE_API_KEY

def get_debounce_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the DeBounce access token from the provided tool configuration or environment.

    Raises:
        ValueError: If the token is not found.
    """
    if tool_config:
        debounce_config = next(
            (item for item in tool_config if item.get("name") == "debounce"), None
        )
        if debounce_config:
            config_map = {
                c["name"]: c["value"]
                for c in debounce_config.get("configuration", [])
                if c
            }
            DEBOUNCE_API_KEY = config_map.get("apiKey")
        else:
            DEBOUNCE_API_KEY = None
    else:
        DEBOUNCE_API_KEY = None

    DEBOUNCE_API_KEY = DEBOUNCE_API_KEY or os.getenv("DEBOUNCE_API_KEY")
    if not DEBOUNCE_API_KEY:
        raise ValueError("DEBOUNCE_API_KEY not found in config or env.")
    return DEBOUNCE_API_KEY

# --------------------------------------------------------------------------------
# 2. Provider-Specific Validation Functions
# --------------------------------------------------------------------------------

@assistant_tool
async def check_email_validity_with_zero_bounce(email_id: str, tool_config: Optional[List[Dict]] = None) -> Dict[str, bool]:
    """
    Validate a single email address using the ZeroBounce API.
    
    Returns:
        dict: {"is_valid": bool}
    """
    ZERO_BOUNCE_API_KEY = get_zero_bounce_access_token(tool_config)
    url = (
        "https://api.zerobounce.net/v2/validate"
        f"?api_key={ZERO_BOUNCE_API_KEY}&email={email_id}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"[ZeroBounce] Error: Received status code {response.status}")
            result = await response.json()

            # ZeroBounce returns status = "valid" when the email is valid
            status = result.get("status", "").lower()
            is_valid = (status == "valid")
            return {"is_valid": is_valid}

@assistant_tool
async def check_email_validity_with_debounce(email_id: str, tool_config: Optional[List[Dict]] = None) -> Dict[str, bool]:
    """
    Validate a single email address using the DeBounce API.

    Returns:
        dict: {"is_valid": bool}
    """
    DEBOUNCE_API_KEY = get_debounce_access_token(tool_config)
    # Example: https://api.debounce.io/v1/?api=YOUR_API_KEY&email=EMAIL
    url = (
        "https://api.debounce.io/v1/"
        f"?api={DEBOUNCE_API_KEY}&email={email_id}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"[DeBounce] Error: Received status code {response.status}")
            result = await response.json()

            # DeBounce nested JSON example:
            # {
            #   "debounce": {
            #     "code": "5",
            #     "reason": "Safe to Send",
            #     ...
            #   }
            # }
            # Code "5" indicates "Safe to Send" => valid
            code = result.get("debounce", {}).get("code")
            is_valid = (code == "5")
            return {"is_valid": is_valid}

# --------------------------------------------------------------------------------
# 3. Tool Mapping and High-Level Function
# --------------------------------------------------------------------------------

allowed_check_email_tools = ["zerobounce", "debounce"]

TOOL_NAME_TO_FUNCTION_MAP = {
    "zerobounce": check_email_validity_with_zero_bounce,
    "debounce": check_email_validity_with_debounce
}

@assistant_tool
async def check_email_validity(
    email_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, bool]:
    """
    Validate an email address by choosing the appropriate tool based on the tool_config.

    Parameters:
        email_id (str): The email address to validate.
        tool_config (Optional[List[Dict]]): Tool configuration to identify which tool is available.

    Returns:
        dict: A standardized JSON with {"is_valid": True/False}.

    Raises:
        ValueError: If no tool configuration or no suitable validation tool is found.
    """
    if not tool_config:
        raise ValueError("No tool configuration found.")

    chosen_tool_func = None
    for item in tool_config:
        name = item.get("name")
        if name in TOOL_NAME_TO_FUNCTION_MAP and name in allowed_check_email_tools:
            chosen_tool_func = TOOL_NAME_TO_FUNCTION_MAP[name]
            break

    if not chosen_tool_func:
        raise ValueError("No suitable email validation tool found in tool_config.")

    return await chosen_tool_func(email_id, tool_config)
