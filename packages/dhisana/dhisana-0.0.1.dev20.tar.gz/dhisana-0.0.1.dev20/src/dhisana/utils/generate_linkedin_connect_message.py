# Import necessary modules
from typing import Dict, List, Optional
from pydantic import BaseModel
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal    

# Define a model for LinkedIn connect message information
class LinkedInConnectMessage(BaseModel):
    subject: str
    body: str

@assistant_tool
async def generate_linkedin_connect_message(user_info: dict, connect_template: str, additional_instructions: str, tool_config: Optional[List[Dict]] = None):
    """
    Generate a LinkedIn connect message using the provided user information and template with placeholders.

    This function sends an asynchronous request to generate a LinkedIn connect message based on the user information and template provided.
    
    Parameters:
    user_info (dict): Information about the user.
    connect_template (str): The connect message template with placeholders.
    additional_instructions (str): Additional instructions for generating the message.
    tool_config (Optional[dict]): Configuration for the tool (default is None).

    Returns:
    dict: The JSON response containing the message subject and body.

    Raises:
    ValueError: If required parameters are missing.
    Exception: If there is an error in processing the request.
    """

    prompt = f"""
    Generate a personalized LinkedIn connection request message using the provided user information. The message should follow the given template and fill in the placeholders <<>>.
    
    Connect Template:
    {connect_template}
    
    Additional Instructions:
    {additional_instructions}
    
    User Information:
    {user_info}
    
    The output should be in JSON format with the following structure:
    {{
        "subject": "Subject of the message.",
        "body": "Body of the message to be sent."
    }}
    """
    response, status = await get_structured_output_internal(prompt, LinkedInConnectMessage, tool_config=tool_config)
    if status != 'SUCCESS':
        raise Exception("Error in generating the LinkedIn connect message.")
    return response.model_dump()

@assistant_tool
async def get_personalized_linkedin_message(lead_info: dict, outreach_context:str, tool_config: Optional[List[Dict]] = None):
    connect_template = f"""
        Hi <<first_name>>,
        << message >>
        Thanks,
        << sender_name >>
    """
    
    response = await generate_linkedin_connect_message(lead_info, connect_template, outreach_context, tool_config=tool_config)
    return response.get("body")