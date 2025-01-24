
import asyncio
import hashlib
import re
import time
import logging
from typing import Dict, List, Optional
import uuid

from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAIError, LengthFinishReasonError
from pydantic import BaseModel, TypeAdapter

from dhisana.utils import cache_output_tools
from dhisana.utils.openai_assistant_and_file_utils import add_user_message, create_and_retrieve_run, create_assistant, create_thread, delete_assistant, get_first_message_content, get_run_status
from dhisana.utils.openai_helpers import get_openai_access_token

# Get structutred output based on input message using OpenAI API
async def get_structured_output_internal(message: str, response_type, tool_config: Optional[List[Dict]] = None):
    try:
        # Use the class name instead of serializing the class
        response_type_str = response_type.__name__
        
        # Create unique hashes for message and response_type
        message_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode('utf-8')).hexdigest()
        
        # Generate the cache key
        cache_key = f"{message_hash}:{response_type_hash}"
        cached_response = cache_output_tools.retrieve_output(f"get_structured_output_internal", cache_key)
        if cached_response is not None:
            parsed_cached_response = response_type.parse_raw(cached_response)
            return parsed_cached_response, 'SUCCESS'
        
        OPENAI_KEY = get_openai_access_token(tool_config)
        client = AsyncOpenAI(api_key=OPENAI_KEY)
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract structured content from input. Output is in JSON Format."},
                {"role": "user", "content": message},
            ],
            response_format=response_type
        )

        response = completion.choices[0].message
        if response.parsed:
            cache_output_tools.cache_output("get_structured_output_internal", cache_key, response.parsed.json())
            return response.parsed, 'SUCCESS'
        elif response.refusal:
            logging.warning("ERROR: Refusal response: %s", response.refusal)
            return response.refusal, 'FAIL'
        
    except LengthFinishReasonError as e:
        logging.error(f"Too many tokens: {e}")
        raise HTTPException(status_code=502, detail="The request exceeded the maximum token limit.")
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")
    
    
async def get_structured_output_with_assistant_and_vector_store(prompt: str, response_format: BaseModel, vector_store_id: str, tool_config: Optional[List[Dict]] = None):
    assistant = None
    try:
        # Step 1: Create an assistant with the specified vector store attached
        assistant_name = "assistant_" + uuid.uuid4().hex
        instructions = "Hi, You are a helpful AI Assistant. Help the users with the given instructions."
        tools = []
        assistant, vector_store_id = await create_assistant(assistant_name, instructions, tools, vector_store_id, tool_config)

        # Step 2: Create a new thread with the user's prompt
        metadata = {"assistant_id": assistant.id, "assistant_name": assistant_name}
        thread = await create_thread(metadata, vector_store_id=vector_store_id, tool_config=tool_config)
        
        message = await add_user_message(prompt, thread, tool_config)
        tools = []

        # Step 3: Initiate a run with the specified response format
        run = await create_and_retrieve_run(thread.id, assistant.id, instructions, tools, response_format, tool_config)

        # Step 4: Poll the run status until completion
        MAX_WAIT_TIME = 180  # 3 minutes in seconds
        start_time = time.time()
        while run.status not in ["completed", "failed"]:
            if time.time() - start_time > MAX_WAIT_TIME:
                logging.error("Run did not complete within the maximum wait time of 3 minutes.")
                break
            await asyncio.sleep(5)
            run = await get_run_status(thread.id, run.id, tool_config)

        # Step 5: Check if the run completed successfully
        if run.status == 'completed':
            # Retrieve the assistant's response
            response_text = await get_first_message_content(thread.id, tool_config)
            pattern = r'【\d+:\d+†[^】]+】'
            response_text = re.sub(pattern, '', response_text)
            if response_text:
                response = TypeAdapter(response_format).validate_json(response_text)
            else:
                raise HTTPException(status_code=502, detail="No response from the assistant.")
            return response, 'SUCCESS'
        else:
            raise HTTPException(status_code=502, detail=f"Run failed with status: {run.status}")

    except LengthFinishReasonError as e:
        logging.error(f"Too many tokens: {e}")
        raise HTTPException(status_code=502, detail="The request exceeded the maximum token limit.")
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")
    finally:
        if assistant:
            await delete_assistant(assistant.id, tool_config)
