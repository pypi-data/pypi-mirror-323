import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import openai
from pydantic import BaseModel

from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.agent_task import execute_task
from dhisana.utils.compose_salesnav_query import generate_salesnav_people_search_url
from dhisana.utils.check_for_intent_signal import check_for_intent_signal
from dhisana.utils.generate_linkedin_connect_message import get_personalized_linkedin_message


class WorkflowPythonCode(BaseModel):
    workflow_python_code: str


async def generate_workflow_code(
    english_description: str,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generate a workflow code given description in plain english.

    :param english_description: A plain-English description of the desired workflow
    :param tool_config: Optional configuration for tools or environment

    :return: Python code to run.
    """

    # Construct a prompt for the LLM
    system_message = (
        "You are a helpful assistant that converts an English description of "
        "Workflow into a workflow excution code in python using excute task. "
        "Your output valid python code as in example blow. "
        "Do not include any additional text or explanation. "
        "If any item is not supported, do the best guess or omit it."
    )

    commands_supported = [
        "view_linked_in_profile",
        "send_connection_request",
        "like_recent_post",
        "send_message",
        "get_current_messages",
    ]

    example_of_workflow_code = (
        """
import asyncio
from dhisana.utils.agent_task import execute_task
from dhisana.utils.compose_salesnav_query import generate_salesnav_people_search_url
from dhisana.utils.check_for_intent_signal import check_for_intent_signal
from dhisana.utils.generate_linkedin_connect_message import get_personalized_linkedin_message

async def custom_workflow(tool_config):    
    # Generate a Sales Navigator query to get a list of relevant leads
    english_request_for_salesnav_search = (
        "Find me 2nd-degree connections who recently changed jobs, "
        "have a current job title of Chief Marketing Officer, "
        "and work in companies with 50-1000 employees."
    )
    example_user_query = ""  # This is example query specified by the user. Keep this empty if not specified
    result = await generate_salesnav_people_search_url(
        english_request_for_salesnav_search, 
        example_user_query, 
        tool_config=tool_config
    )
    salesnav_url_list_leads = result.get('linkedin_salenav_url_with_query_parameters')  
    
    # Extract leads information using the generated Sales Navigator URL
    MAX_PAGES_TO_FETCH = 1  # MAX_PAGES_TO_FETCH can go up to 90. Default is 1. Each page contains 25 leads.
    command_name = "extract_leads_information"
    command_args = {"salesnav_url_list_leads": salesnav_url_list_leads, "max_pages": MAX_PAGES_TO_FETCH}
    result = await execute_task(command_name, command_args, tool_config=tool_config)
    
    leads = result.get('data', []) if result and result.get('data') else []
    if not leads:
        return "SUCCESS"
    
    # Filter and deduplicate leads with valid lead_salesnav_url
    unique_leads = {lead['lead_salesnav_url']: lead for lead in leads if lead.get("lead_salesnav_url")}
    unique_leads = list(unique_leads.values())
    if not unique_leads:
        return "SUCCESS"
    
    # Qualify leads based on intent signals
    qualified_leads = []
    for lead in unique_leads:
        # Check if the current company uses Adobe in their tech stack
        current_company_technology_intent_score = await check_for_intent_signal(
            lead=lead, 
            signal_to_look_for_in_plan_english="Check if the current company uses Adobe in their tech stack.", 
            intent_signal_type="technology_used_by_current_company", 
            tool_config=tool_config
        )
        
        # Check if the previous company used Adobe in their tech stack
        previous_company_technology_intent_score = await check_for_intent_signal(
            lead=lead, 
            signal_to_look_for_in_plan_english="Check if the previous company used Adobe in their tech stack.", 
            intent_signal_type="technology_used_by_previous_company", 
            tool_config=tool_config
        )
        
        # Check if the lead recently changed companies
        recent_job_change_intent_score = await check_for_intent_signal(
            lead=lead, 
            signal_to_look_for_in_plan_english="Check if the lead recently changed companies.", 
            intent_signal_type="recent_job_change", 
            tool_config=tool_config
        )
        # Qualify leads based on specific conditions
        if (
            recent_job_change_intent_score > 3 and 
            current_company_technology_intent_score == 0 and 
            previous_company_technology_intent_score > 3
        ):
            qualified_leads.append(lead)

    # Limit processing to avoid LinkedIn limits
    MAX_ENTRIES_TO_PROCESS = 100
    qualified_leads = qualified_leads[:MAX_ENTRIES_TO_PROCESS]
    
    # Interact with qualified leads on LinkedIn Sales Navigator
    # Stay within sales navigator limits
    MAX_ACTIONS = {
        "view_profile": 30,
        "send_connection_request": 10,
        "send_message": 10,
        "like_post": 10
    }
    
    for lead in qualified_leads[:MAX_ACTIONS["view_profile"]]:
        await execute_task(
            command_name="view_linked_in_profile", 
            command_args={"salesnav_url_profile": lead.get("lead_salesnav_url")}, 
            tool_config=tool_config
        )
    
    for lead in qualified_leads[:MAX_ACTIONS["send_connection_request"]]:
        await execute_task(
            command_name="send_connection_request", 
            command_args={"salesnav_url_profile": lead.get("lead_salesnav_url")}, 
            tool_config=tool_config
        )
    
    for lead in qualified_leads[:MAX_ACTIONS["send_message"]]:
        context = "<< Fill in context that can be used to generate message>>"  # Fill in campaign context in which the message is being sent
        message_to_send = await get_personalized_linkedin_message(lead_info=lead, outreach_context=context, tool_config=tool_config)
        await execute_task(
            command_name="send_message", 
            command_args={"salesnav_url_profile": lead.get("lead_salesnav_url"), "message": message_to_send}, 
            tool_config=tool_config
        )
    
    for lead in qualified_leads[:MAX_ACTIONS["like_post"]]:
        await execute_task(
            command_name="like_recent_post", 
            command_args={"salesnav_url_profile": lead.get("lead_salesnav_url")}, 
            tool_config=tool_config
        )
    
    return "SUCCESS"
"""
    )

    user_prompt = f"""
    {system_message}
    The user wants to generate a workflow code in python that performs the following:

    "{english_description}"

    The supported command_name are described below (for your reference):

    {commands_supported}
    
    Following Example of a workflow python code that searches for users on sales navigator, qualifies them based on intent signals, and interacts with them on LinkedIn Sales Navigator.:
    {example_of_workflow_code}
    
    Each lead returned has the following fields in the dicionary:
    
    full_name, first_name, last_name, email, lead_salesnav_url, company_salesnav_url,
    user_linkedin_url, primary_domain_of_organization, job_title, phone, headline,
    lead_location, organization_name, organization_website, summary_about_lead, keywords,
    number_of_linkedin_connections
    
    Generate valid python code in workflow_python_code. 
    Use the example provided as a reference on how to generate the workflow code.
    Double check to ensure the code generated is valid.
    Output is in valid JSON format.
    """

    response, status = await get_structured_output_internal(
        user_prompt, WorkflowPythonCode, tool_config=tool_config
    )
    return response.model_dump(), status


async def generate_workflow_and_execute(
    user_query: str, tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Generate workflow from user query in natural language and execute the same.

    Args:
        user_query (str): User query in natural language.
        tool_config (Optional[List[Dict]]): List of config dictionaries.

    Returns:
        str: A JSON string representing the FileList containing the path to 
             the output file if created, or an error message if an error occurred.
    """
    response, status = await generate_workflow_code(user_query, tool_config=tool_config)
    if status == 'SUCCESS' and response and response.get('workflow_python_code'):
        code = response.get('workflow_python_code')
        print("Generated code:\n", code)
        local_vars = {}
        global_vars = {}

        try:
            ## Fill this code here to 
            # Now we should have `custom_workflow` in local_vars
            # exec(code, global_vars, local_vars)
            exec(code, globals(), local_vars)
            custom_workflow_fn = local_vars.get("custom_workflow", None)
            if custom_workflow_fn is None:
                raise RuntimeError("No custom_workflow function found in generated code")

            async def run_custom_workflow(tool_cfg):
                return await custom_workflow_fn(tool_cfg)
            result = await run_custom_workflow(tool_config)
            if result is None or result != "SUCCESS":
                return json.dumps({"error": "Error in runnig the workflow code.", "status": status})
            return json.dumps({"status": result})
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)})
    return json.dumps({"error": "No workflow code generated.", "status": status})