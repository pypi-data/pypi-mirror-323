# Functions to handle google workspace tools like google drive, gmail, calendar etc.
import os
import json
import uuid
import io
import base64
import logging
from typing import List, Dict, Any, Optional
import httpx
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import datetime
from dhisana.utils.assistant_tool_tag import assistant_tool

#Tools to work with google workspace like drive, calendar, gmail etc.

def get_google_workspace_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the GOOGLE_SERVICE_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The GOOGLE_SERVICE_KEY access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    if tool_config:
        google_workspace_config = next(
            (item for item in tool_config if item.get("name") == "googleworkspace"), None
        )
        if google_workspace_config:
            config_map = {
                item["name"]: item["value"]
                for item in google_workspace_config.get("configuration", [])
                if item
            }
            GOOGLE_SERVICE_KEY = config_map.get("apiKey")
        else:
            GOOGLE_SERVICE_KEY = None
    else:
        GOOGLE_SERVICE_KEY = None

    GOOGLE_SERVICE_KEY = GOOGLE_SERVICE_KEY or os.getenv("GOOGLE_SERVICE_KEY")
    if not GOOGLE_SERVICE_KEY:
        raise ValueError("GOOGLE_SERVICE_KEY access token not found in tool_config or environment variable")
    return GOOGLE_SERVICE_KEY

def get_google_automation_email(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the EMAIL_FOR_AUTOMATION used for the access.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The EMAIL_FOR_AUTOMATION access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    if tool_config:
        google_workspace_config = next(
            (item for item in tool_config if item.get("name") == "googleworkspace"), None
        )
        if google_workspace_config:
            config_map = {
                item["name"]: item["value"]
                for item in google_workspace_config.get("configuration", [])
                if item
            }
            EMAIL_FOR_AUTOMATION = config_map.get("googleEmailForAutomation")
        else:
            EMAIL_FOR_AUTOMATION = None
    else:
        EMAIL_FOR_AUTOMATION = None

    EMAIL_FOR_AUTOMATION = EMAIL_FOR_AUTOMATION or os.getenv("EMAIL_FOR_AUTOMATION")
    if not EMAIL_FOR_AUTOMATION:
        raise ValueError("EMAIL_FOR_AUTOMATION access token not found in tool_config or environment variable")
    return EMAIL_FOR_AUTOMATION

def convert_base_64_json(base64_string):
    """
    Convert a base64 encoded string to a JSON string.

    Args:
        base64_string (str): The base64 encoded string.

    Returns:
        str: The decoded JSON string.
    """
    # Decode the base64 string to bytes
    decoded_bytes = base64.b64decode(base64_string)

    # Convert bytes to JSON string
    json_string = decoded_bytes.decode('utf-8')

    return json_string

@assistant_tool
async def get_file_content_from_googledrive_by_name(file_name: str = None, tool_config: Optional[List[Dict]] = None) -> str:
    """
    Searches for a file by name in Google Drive using a service account, downloads it, 
    saves it in /tmp with a unique filename, and returns the local file path.

    :param file_name: The name of the file to search for and download from Google Drive.
    :return: Local file path of the downloaded file.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for Google Drive API access
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Authenticate using the service account info and impersonate the specific email
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(email_for_automation)

    # Build the Google Drive service object
    service = build('drive', 'v3', credentials=credentials)

    # Search for the file by name
    query = f"name = '{file_name}'"
    results = service.files().list(q=query, pageSize=1,
                                   fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        raise FileNotFoundError(f"No file found with the name: {file_name}")

    # Get the file ID of the first matching file
    file_id = items[0]['id']
    file_name = items[0]['name']

    # Create a unique filename by appending a UUID to the original file name
    unique_filename = f"{uuid.uuid4()}_{file_name}"

    # Path to save the downloaded file
    local_file_path = os.path.join('/tmp', unique_filename)

    # Request the file content from Google Drive
    request = service.files().get_media(fileId=file_id)

    # Create a file-like object in memory to hold the downloaded data
    fh = io.FileIO(local_file_path, 'wb')

    # Initialize the downloader
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        logging.info(f"{file_name} Download {int(status.progress() * 100)}%.")

    # Close the file handle
    fh.close()

    # Return the local file path
    return local_file_path


@assistant_tool
async def write_content_to_googledrive(cloud_file_path: str, local_file_path: str, tool_config: Optional[List[Dict]] = None) -> str:
    try:
        """
        Writes content from a local file to a file in Google Drive using a service account.
        If the file does not exist in Google Drive, it creates it along with any necessary intermediate directories.
        
        :param cloud_file_path: The path of the file to create or update on Google Drive.
        :param local_file_path: The path to the local file whose content will be uploaded.
        :return: The file ID of the uploaded or updated file.
        """

        # Retrieve the service account JSON and email for automation from environment variables
        service_account_base64 = get_google_workspace_token(tool_config)
        email_for_automation = get_google_automation_email(tool_config)
        service_account_json = convert_base_64_json(service_account_base64)

        # Parse the JSON string into a dictionary
        service_account_info = json.loads(service_account_json)

        # Define the required scope for Google Drive API access
        SCOPES = ['https://www.googleapis.com/auth/drive']

        # Authenticate using the service account info and impersonate the specific email
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        ).with_subject(email_for_automation)

        # Build the Google Drive service object
        service = build('drive', 'v3', credentials=credentials)

        # Split the cloud file path into components
        path_components = cloud_file_path.split('/')
        parent_id = 'root'
        
        # Create intermediate directories if they don't exist
        for component in path_components[:-1]:
            query = f"'{parent_id}' in parents and name = '{component}' and mimeType = 'application/vnd.google-apps.folder'"
            results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
            items = results.get('files', [])
            
            if items:
                parent_id = items[0]['id']
            else:
                file_metadata = {
                    'name': component,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                parent_id = folder.get('id')

        # Prepare the file for upload
        media_body = MediaFileUpload(local_file_path, resumable=True)
        file_name = path_components[-1]

        # Check if the file exists in the specified directory
        query = f"'{parent_id}' in parents and name = '{file_name}'"
        results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if items:
            # File exists, update its content
            file_id = items[0]['id']
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media_body
            ).execute()
        else:
            # File does not exist, create a new one
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            created_file = service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id'
            ).execute()
            file_id = created_file.get('id')
    except HttpError as error:
            raise Exception(f"list_files_in_drive_folder_by_name An error occurred: {error}")

    return file_id

@assistant_tool
async def list_files_in_drive_folder_by_name(folder_path: str = None, tool_config: Optional[List[Dict]] = None) -> List[str]:
    """
    Lists all files in the given Google Drive folder by folder path.
    If no folder path is provided, it lists files in the root folder.

    :param folder_path: The path of the folder in Google Drive to list files from.
                        Example: '/manda_agent_metadata/openapi_tool_specs/'
    :return: A list of file names in the folder.
    :raises Exception: If any error occurs during the process.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_workspace_token(tool_config)
    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for Google Drive API access
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Authenticate using the service account info and impersonate the specific email
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(email_for_automation)

    # Build the Google Drive service object
    service = build('drive', 'v3', credentials=credentials)

    folder_id = 'root'  # Start from root if folder_path is None

    if folder_path:
        # Split the folder path into individual folder names
        folder_names = [name for name in folder_path.strip(
            '/').split('/') if name]
        for folder_name in folder_names:
            # Search for the folder by name under the current folder_id
            query = (
                f"name = '{
                    folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
                f"and '{folder_id}' in parents and trashed = false"
            )
            try:
                results = service.files().list(
                    q=query,
                    pageSize=1,
                    fields="files(id, name)"
                ).execute()
                items = results.get('files', [])
                if not items:
                    raise FileNotFoundError(
                        f"Folder '{folder_name}' not found under parent folder ID '{folder_id}'"                           
                    )
                # Update folder_id to the ID of the found folder
                folder_id = items[0]['id']
            except HttpError as error:
                raise Exception(f"list_files_in_drive_folder_by_name An error occurred: {error}")

    # Now folder_id is the ID of the desired folder
    # List all files in the specified folder
    query = f"'{folder_id}' in parents and trashed = false"
    try:
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields="files(id, name)"
        ).execute()
        items = results.get('files', [])
        # Extract file names
        file_names = [item['name'] for item in items]
        return file_names
    except HttpError as error:
        raise Exception(f"list_files_in_drive_folder_by_name An error occurred while listing files: {error}")


@assistant_tool
async def send_email_using_service_account_async(
    recipient: str, subject: str, body: str, tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Asynchronously sends an email using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender.

    :param recipient: The email address of the recipient.
    :param subject: The subject of the email.
    :param body: The body text of the email.
    :return: The ID of the sent message.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_workspace_token(tool_config)

    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for sending email via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(email_for_automation)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint for sending messages
    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'

    # Create the email message
    message = MIMEText(body)
    message['to'] = recipient
    message['from'] = email_for_automation
    message['subject'] = subject

    # Encode the message in base64url format
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Prepare the request payload
    payload = {
        'raw': raw_message
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(gmail_api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        sent_message = response.json()

    # Return the message ID of the sent email
    return sent_message.get('id', 'No ID returned')

@assistant_tool
async def list_emails_in_time_range_async(start_time: str, 
                                          end_time: str, 
                                          unread_only: bool = True, 
                                          labels: List[str] = [], 
                                          mailbox_email: str = "",
                                          tool_config: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """
    Asynchronously lists emails in a given time range using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender.

    :param start_time: The start time in RFC 3339 format (e.g., '2021-01-01T00:00:00Z').
    :param end_time: The end time in RFC 3339 format (e.g., '2021-01-31T23:59:59Z').
    :param unread_only: If True, only return unread emails.
    :param labels: Optional list of labels to filter the emails.
    :param mailbox_email: Optional email address to use for the mailbox. Must be in the allowed list.
    :return: A list of email message details.
    """

    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    allowed_emails_for_automation = email_for_automation.split(",")
    if not allowed_emails_for_automation:
        raise EnvironmentError("No allowed emails for automation found in environment variables.")

    # Check if mailbox_email is provided and is in the allowed list
    if mailbox_email:
        if mailbox_email not in allowed_emails_for_automation:
            raise ValueError(f"The provided mailbox_email '{mailbox_email}' is not in the allowed list for automation.")
    else:
        mailbox_email = allowed_emails_for_automation[0]

    # Function to convert base64-encoded JSON to a string
    def convert_base_64_json(base64_json: str) -> str:
        return base64.b64decode(base64_json).decode('utf-8')

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for reading emails via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(mailbox_email)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint for listing messages
    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'

    # Convert the RFC 3339 formatted times to Unix epoch timestamps
    start_timestamp = int(datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00')).timestamp())
    end_timestamp = int(datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00')).timestamp())

    # Create the query parameters for the time range using Unix epoch timestamps
    query = f'after:{start_timestamp} before:{end_timestamp}'

    # Add 'is:unread' to the query if unread_only is True
    if unread_only:
        query += ' is:unread'

    # Add labels to the query if provided
    if labels:
        label_query = ' '.join([f'label:{label}' for label in labels])
        query += f' {label_query}'

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Prepare the parameters
    params = {
        'q': query
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        messages = response.json().get('messages', [])

        email_details = []
        for message in messages:
            message_id = message['id']
            message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'
            message_response = await client.get(message_url, headers=headers)
            message_response.raise_for_status()
            message_data = message_response.json()

            email_details.append({
                "mailbox_email_id": message_data['id'],
                "message_id": message_data['threadId'],
                "email_subject": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Subject'), None),
                "email_sender": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'From'), None),
                "email_recipients": [header['value'] for header in message_data['payload']['headers'] if header['name'] in ['To', 'Cc', 'Bcc']],
                "email_date": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Date'), None),
                "read_email_status": 'UNREAD' if 'UNREAD' in message_data['labelIds'] else 'READ',
                "email_labels": message_data.get('labelIds', [])
            })

    return email_details


@assistant_tool
async def fetch_last_n_sent_messages(recipient_email: str, 
                                     num_messages: int,
                                     tool_config: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """
    Fetch the last n messages sent to a specific recipient using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender.

    :param recipient_email: The recipient's email address.
    :param num_messages: The number of recent messages to fetch.
    :return: A list of email message details.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    allowed_emails_for_automation = email_for_automation.split(",")
    if not allowed_emails_for_automation:
        raise EnvironmentError("No allowed emails for automation found in environment variables.")

    mailbox_email = allowed_emails_for_automation[0]

    # Function to convert base64-encoded JSON to a string
    def convert_base_64_json(base64_json: str) -> str:
        return base64.b64decode(base64_json).decode('utf-8')

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for reading emails via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(mailbox_email)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint for listing messages
    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'

    # Create the query parameters for the recipient email
    query = f'to:{recipient_email}'

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Prepare the parameters
    params = {
        'q': query,
        'maxResults': num_messages
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        messages = response.json().get('messages', [])

        email_details = []
        for message in messages:
            message_id = message['id']
            message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'
            message_response = await client.get(message_url, headers=headers)
            message_response.raise_for_status()
            message_data = message_response.json()

            email_details.append({
                "mailbox_email_id": message_data['id'],
                "message_id": message_data['threadId'],
                "email_subject": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Subject'), None),
                "email_sender": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'From'), None),
                "email_recipients": [header['value'] for header in message_data['payload']['headers'] if header['name'] in ['To', 'Cc', 'Bcc']],
                "email_date": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Date'), None),
                "read_email_status": 'UNREAD' if 'UNREAD' in message_data['labelIds'] else 'READ',
                "email_labels": message_data.get('labelIds', [])
            })

    return email_details

@assistant_tool
async def fetch_last_n_received_messages(sender_email: str, 
                                         num_messages: int,
                                         tool_config: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """
    Fetch the last n messages received from a specific sender using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the recipient.

    :param sender_email: The sender's email address.
    :param num_messages: The number of recent messages to fetch.
    :return: A list of email message details.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    allowed_emails_for_automation = email_for_automation.split(",")
    if not allowed_emails_for_automation:
        raise EnvironmentError("No allowed emails for automation found in environment variables.")

    mailbox_email = allowed_emails_for_automation[0]

    # Function to convert base64-encoded JSON to a string
    def convert_base_64_json(base64_json: str) -> str:
        return base64.b64decode(base64_json).decode('utf-8')

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for reading emails via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(mailbox_email)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint for listing messages
    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'

    # Create the query parameters for the sender email
    query = f'from:{sender_email}'

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Prepare the parameters
    params = {
        'q': query,
        'maxResults': num_messages
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        messages = response.json().get('messages', [])

        email_details = []
        for message in messages:
            message_id = message['id']
            message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'
            message_response = await client.get(message_url, headers=headers)
            message_response.raise_for_status()
            message_data = message_response.json()

            email_details.append({
                "mailbox_email_id": message_data['id'],
                "message_id": message_data['threadId'],
                "email_subject": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Subject'), None),
                "email_sender": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'From'), None),
                "email_recipients": [header['value'] for header in message_data['payload']['headers'] if header['name'] in ['To', 'Cc', 'Bcc']],
                "email_date": next((header['value'] for header in message_data['payload']['headers'] if header['name'] == 'Date'), None),
                "read_email_status": 'UNREAD' if 'UNREAD' in message_data['labelIds'] else 'READ',
                "email_labels": message_data.get('labelIds', [])
            })

    return email_details


@assistant_tool
async def get_email_details_async(message_id: str, 
                                  mailbox_email: str = "",
                                  tool_config: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Asynchronously retrieves the full details of an email using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the user.

    :param message_id: The ID of the email message to retrieve.
    :param mailbox_email: Optional email address to use for the mailbox. Must be in the allowed list.
    :return: A dictionary containing the full message details in JSON format.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    allowed_emails_for_automation = email_for_automation.split(",")
    if not allowed_emails_for_automation:
        raise EnvironmentError("No allowed emails for automation found in environment variables.")

    # Check if mailbox_email is provided and is in the allowed list
    if mailbox_email:
        if mailbox_email not in allowed_emails_for_automation:
            raise ValueError(f"The provided mailbox_email '{mailbox_email}' is not in the allowed list for automation.")
    else:
        mailbox_email = allowed_emails_for_automation[0]

    # Function to convert base64-encoded JSON to a string
    def convert_base_64_json(base64_json: str) -> str:
        return base64.b64decode(base64_json).decode('utf-8')

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for reading emails via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(mailbox_email)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint for getting a message
    gmail_api_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Prepare the parameters
    params = {
        'format': 'full'
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        message_details = response.json()

    # Return the full message JSON
    return message_details

@assistant_tool
async def reply_to_email_async(message_id: str, 
                               reply_body: str, 
                               mailbox_email: str = "", 
                               mark_as_read: str = "True", 
                               add_labels: List[str] = [],
                               tool_config: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Asynchronously replies to an email with reply_all using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender.

    :param message_id: The ID of the email message to reply to.
    :param reply_body: The body text of the reply email.
    :param mailbox_email: Optional email address to use for the mailbox. Must be in the allowed list.
    :param mark_as_read: If True, mark the email thread as read after replying.
    :param add_labels: Optional list of labels to add to the email thread.
    :return: A dictionary containing the details of the sent message.
    """
    # Retrieve the service account JSON and email for automation from environment variables
    service_account_base64 = get_google_workspace_token(tool_config)
    email_for_automation = get_google_automation_email(tool_config)
    if not service_account_base64 or not email_for_automation:
        raise EnvironmentError("Required environment variables are not set.")

    allowed_emails_for_automation = email_for_automation.split(",")
    if not allowed_emails_for_automation:
        raise EnvironmentError("No allowed emails for automation found in environment variables.")

    # Check if mailbox_email is provided and is in the allowed list
    if mailbox_email:
        if mailbox_email not in allowed_emails_for_automation:
            raise ValueError(f"The provided mailbox_email '{mailbox_email}' is not in the allowed list for automation.")
    else:
        mailbox_email = allowed_emails_for_automation[0]

    # Function to convert base64-encoded JSON to a string
    def convert_base_64_json(base64_json: str) -> str:
        return base64.b64decode(base64_json).decode('utf-8')

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required scope for sending email via Gmail API
    SCOPES = ['https://mail.google.com/']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(mailbox_email)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the Gmail API endpoint
    gmail_api_base_url = 'https://gmail.googleapis.com/gmail/v1/users/me'

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Retrieve the original message
    get_message_url = f'{gmail_api_base_url}/messages/{message_id}'
    params = {
        'format': 'full'
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(get_message_url, headers=headers, params=params)
        response.raise_for_status()
        original_message = response.json()

    # Extract headers from the original message
    headers_list = original_message.get('payload', {}).get('headers', [])
    headers_dict = {header['name']: header['value'] for header in headers_list}
    thread_id = original_message.get('threadId')

    # Prepare reply headers
    subject = headers_dict.get('Subject', '')
    if not subject.startswith('Re:'):
        subject = f'Re: {subject}'

    to_addresses = headers_dict.get('From', '')
    cc_addresses = headers_dict.get('Cc', '')
    message_id_header = headers_dict.get('Message-ID', '')

    # Create the email message
    message = MIMEText(reply_body)
    message['To'] = to_addresses
    if cc_addresses:
        message['Cc'] = cc_addresses
    message['From'] = mailbox_email
    message['Subject'] = subject
    message['In-Reply-To'] = message_id_header
    message['References'] = message_id_header

    # Encode the message in base64url format
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Prepare the request payload
    payload = {
        'raw': raw_message,
        'threadId': thread_id
    }

    send_message_url = f'{gmail_api_base_url}/messages/send'

    async with httpx.AsyncClient() as client:
        response = await client.post(send_message_url, headers=headers, json=payload)
        response.raise_for_status()
        sent_message = response.json()

    # Mark the thread as read if mark_as_read is True
    if mark_as_read.lower() == "true":
        modify_thread_url = f'{gmail_api_base_url}/threads/{thread_id}/modify'
        modify_payload = {
            'removeLabelIds': ['UNREAD']
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(modify_thread_url, headers=headers, json=modify_payload)
            response.raise_for_status()

    # Add labels to the thread if add_labels is not empty
    if add_labels:
        modify_thread_url = f'{gmail_api_base_url}/threads/{thread_id}/modify'
        modify_payload = {
            'addLabelIds': add_labels
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(modify_thread_url, headers=headers, json=modify_payload)
            response.raise_for_status()

    # Extract details of the sent message
    sent_message_details = {
        "mailbox_email_id": sent_message['id'],
        "message_id": sent_message['threadId'],
        "email_subject": subject,
        "email_sender": mailbox_email,
        "email_recipients": [to_addresses] + ([cc_addresses] if cc_addresses else []),
        "read_email_status": 'READ' if mark_as_read.lower() == "true" else 'UNREAD',
        "email_labels": sent_message.get('labelIds', [])
    }

    # Return the details of the sent email
    return sent_message_details


@assistant_tool
async def get_calendar_events_using_service_account_async(
    start_date: str, end_date: str, tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Asynchronously retrieves a list of events from a user's Google Calendar using a service account.
    The service account must have domain-wide delegation to impersonate the user.
    Events are filtered based on the provided start and end date range.

    :param start_date: The start date (inclusive) to filter events. Format: 'YYYY-MM-DD'.
    :param end_date: The end date (exclusive) to filter events. Format: 'YYYY-MM-DD'.
    :return: A list of calendar events within the specified date range.
    """
    # Helper function to decode base64 JSON
    def convert_base_64_json(encoded_json: str) -> str:
        decoded_bytes = base64.b64decode(encoded_json)
        return decoded_bytes.decode('utf-8')

    # Retrieve the service account JSON and email for automation from environment variables
    email_for_automation = os.getenv('EMAIL_FOR_AUTOMATION')
    service_account_base64 = os.getenv('GOOGLE_SERVICE_KEY')

    if not email_for_automation or not service_account_base64:
        raise EnvironmentError("Required environment variables are not set.")

    service_account_json = convert_base_64_json(service_account_base64)

    # Parse the JSON string into a dictionary
    service_account_info = json.loads(service_account_json)

    # Define the required Google Calendar API scope
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    # Authenticate using the service account info and impersonate the email for automation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    ).with_subject(email_for_automation)

    # Refresh the token if necessary
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Define the API endpoint
    calendar_api_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'

    # Convert start and end dates to ISO 8601 format with time
    start_datetime = f'{start_date}T00:00:00Z'  # UTC format
    end_datetime = f'{end_date}T23:59:59Z'      # UTC format

    params = {
        'timeMin': start_datetime,
        'timeMax': end_datetime,
        'maxResults': 10,
        'singleEvents': True,
        'orderBy': 'startTime'
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(calendar_api_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        events_result = response.json()

    events = events_result.get('items', [])

    if not events:
        logging.info('No upcoming events found within the specified range.')
    else:
        logging.info('Upcoming events:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            logging.info(f"{start} - {event.get('summary', 'No Title')}")

    return events
