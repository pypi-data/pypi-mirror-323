from typing import Dict, List, Optional
import random

from pydantic import BaseModel

from dhisana.utils.generate_structured_output_internal import get_structured_output_internal

class IntentSignalBasedScoring(BaseModel):
    score_based_on_intent_signal: float
    
async def check_for_intent_signal(
    lead: dict,
    signal_to_look_for_in_plan_english: str, 
    intent_signal_type: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict:
    """
    Score the lead based on the intent signal you are looking for 0-5.

    Args:
        lead (dict): Input lead information.
        signal_to_look_for_in_plan_english (str): Signal to look for in plan (in English).
        intent_signal_type (str): Type of intent signal. Can be one of:
            1. "recent_job_change"
            2. "technology_used_by_company"
            3. "recent_news_about_company"
            4. "recent_news_about_lead"
            5. "job_posting_for_role"
            6. "role_with_specific_title_in_company"
            7. "funding_related_news"
            8. "any_other_signal_described_in_input"
        tool_config (Optional[List[Dict]]): Configuration for the tool (default is None).

    Returns:
        int: Score based on the intent signal user is looking for.
    """
    
    user_prompt = f"""
    Hi AI Assistant,
    You are an expert in scoring leads based on intent signals.
    You have the following lead and user requirements to provide a score based on the intent signal you are looking for.
    Provide a score between 0-5 based on the intent signal user is looking for.
    "{lead}"

    Description of the signal user is looking for:

    {signal_to_look_for_in_plan_english}
    
    Based on the input, provide a score between 0-5 in score_based_on_intent_signal.
    Output is in valid JSON format.
    """

    response, status = await get_structured_output_internal(user_prompt, IntentSignalBasedScoring, tool_config=tool_config)
    if status != 'SUCCESS':
        raise Exception("Error in generating the response.")
    return response.score_based_on_intent_signal