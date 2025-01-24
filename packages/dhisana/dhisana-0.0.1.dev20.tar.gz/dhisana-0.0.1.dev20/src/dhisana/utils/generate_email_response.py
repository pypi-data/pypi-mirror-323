# Import necessary modules
import base64
import os
from typing import Any, Dict, List, Optional
import aiohttp
from pydantic import BaseModel
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal    

# Define a model for email response information
class EmailResponse(BaseModel):
    response_message: str
    response_action_to_take: str


# Generate resopnse for a given email message. Use the user information, email teamplte example, and additional instructions context to generate the same.
@assistant_tool
async def generate_email_response(user_info: dict, input_email_message: str, additional_instructions: str, tool_config: Optional[List[Dict]] = None):
    """
    Generate a response for a given email message and determine the action to take.

    This function sends an asynchronous request to generate an email response based on the user information and provided template.
    
    Parameters:
    user_info (dict): Information about the user who needs to be responded to.
    input_email_message (str): The email message to respond to.
    additional_instructions (str): Additional instructions for generating the email (Context to LLM).
    tool_config (Optional[dict]): Configuration for the tool.

    Returns:
    dict: The JSON response containing the email response message and action to take.

    Raises:
    ValueError: If required parameters are missing.
    Exception: If there is an error in processing the request.
    """

    prompt = f"""
    Generate a response to the following email message:
    
    Email message to respond to:
    {input_email_message}
    
    Additional Instructions:
    {additional_instructions}
    
    User Information:
    {user_info}
    
    The output should be in JSON format with the following structure:
    {{
        "response_message": "Response to the email.",
        "response_action_to_take": "One of the following actions: SCHEDULE_MEETING, SEND_REPLY, UNSUBSCRIBE, OOF_MESSAGE, NOT_INTERESTED, NEED_MORE_INFO, FORWARD_TO_OTHER_USER, NO_MORE_IN_ORGANIZATION, OBJECTION_RAISED, OTHER"
    }}
    """
    response, status = await get_structured_output_internal(prompt, EmailResponse, tool_config=tool_config)
    if status != 'SUCCESS':
        raise Exception("Error in generating the email response.")
    return response.model_dump()


@assistant_tool
def extract_email_content_for_llm(email_details: Dict[str, Any]) -> str:
    """
    Cleanup and extracts and formats the required text content from the email details for LLM input.
    
    :param email_details: A dictionary containing the full message details in JSON format.
    :return: A formatted string containing the thread with sender, receiver, date, and message subject.
    """
    # Helper function to decode base64 encoded email body
    def decode_base64(data: str) -> str:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')

    # Extract headers
    headers = {header['name']: header['value'] for header in email_details['payload']['headers']}
    
    # Extract required fields
    sender = headers.get('From', 'Unknown Sender')
    receiver = headers.get('To', 'Unknown Receiver')
    date = headers.get('Date', 'Unknown Date')
    subject = headers.get('Subject', 'No Subject')
    
    # Extract the email body
    body = ""
    if 'parts' in email_details['payload']:
        for part in email_details['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = decode_base64(part['body']['data'])
                break
    else:
        body = decode_base64(email_details['payload']['body']['data'])
    
    # Format the extracted information
    formatted_content = f"From: {sender}\nTo: {receiver}\nDate: {date}\nSubject: {subject}\n\n{body}"
    
    return formatted_content