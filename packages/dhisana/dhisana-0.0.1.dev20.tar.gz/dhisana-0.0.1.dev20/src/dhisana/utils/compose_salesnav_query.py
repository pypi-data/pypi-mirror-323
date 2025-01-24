import asyncio
import os
from typing import Any, Dict, List, Optional
import openai
from pydantic import BaseModel

from dhisana.utils.generate_structured_output_internal import get_structured_output_internal


class SalesNavQuery(BaseModel):
    linkedin_salenav_url_with_query_parameters: str
    
async def generate_salesnav_people_search_url(english_description: str, example_query:str = "", tool_config: Optional[List[Dict[str, Any]]] = None) -> dict[str, Any]:
    """
    Generate a LinkedIn Sales Navigator URL from a plain-English query 
    describing the desired filters and parameters.

    :param english_description: A plain-English description of the desired filters, 
                               e.g. "Find me 2nd-degree connections who changed jobs 
                               recently, speak English, and are in the IT industry."

    :return: A string representing a fully qualified Sales Navigator URL that, 
             when opened, applies the specified filters.
    """

    # You could store a reference list of the supported filters for clarity.
    # This might help the model do a better job, especially if you have repeated usage.
    #OTOD get multiple filter examples and show here.
    supported_filters_explanation = """
    Sales Navigator filters include:
        PAST_COLLEAGUE: Filter for past colleagues.
        CURRENT_TITLE: Filter by current job title.
        PAST_TITLE: Filter by past job title.
        CURRENT_COMPANY: Filter by current company.
        PAST_COMPANY: Filter by past company.
        GEOGRAPHY: Filter by location (country, region, city, postal code).
        INDUSTRY: Filter by industry.
        SCHOOL: Filter by educational institution.
        CONNECTION: Filter by the degree of connection (1st, 2nd, 3rd).
        CONNECTIONS_OF: Filter by people connected to a specific individual.
        GROUP: Filter by LinkedIn group membership.
        COMPANY_HEADCOUNT: Filter by company size.
        COMPANY_TYPE: Filter by the type of company (e.g., public, private).
        SENIORITY_LEVEL: Filter by seniority level (e.g., CXO, Manager).
        YEARS_IN_POSITION: Filter by years in the current position.
        YEARS_IN_COMPANY: Filter by years in the current company.
        FOLLOWING_YOUR_COMPANY: Filter leads who follow your company.
        VIEWED_YOUR_PROFILE: Filter leads who have viewed your LinkedIn profile recently.
        CHANGED_JOBS: Filter leads who have changed jobs in the last 90 days.
        POSTED_ON_LINKEDIN: Filter leads who have posted on LinkedIn recently.
        MENTIONED_IN_NEWS: Filter leads mentioned in recent news.
        TECHNOLOGIES_USED: Filter companies using specific technologies.
        ANNUAL_REVENUE: Filter companies based on revenue range.
    """

    # Construct a prompt for the LLM
    system_message = (
        "You are a helpful AI Assistant that converts an English description of "
        "LinkedIn Sales Navigator search requirements into a valid LinkedIn Sales Navigator people-search URL. "
        "Your output MUST be a single valid URL with properly encoded parameters. "
        "Do not include any additional text or explanation. "
        "If any item is not supported, do the best guess or omit it."
    )
    
    few_examples_of_queries = (
        "\n 1. Below is an example search url with filter --  company headcount 11-500, seniority level CXO, Current Job Title Chief Marketing Officer," 
        "Geography United States, Connection 2nd-degree connections, and Recently Changed jobs: \n"
        "\nhttps://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4390717732%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList"
        "((id%3AC%2Ctext%3A11-50%2CselectionType%3AINCLUDED)%2C(id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)))%2C(type%3AREGION%2Cvalues%3AList"
        "((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARECENTLY_CHANGED_JOBS%2Cvalues%3AList((id%3ARPC%2Ctext%3AChanged%2520jobs%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AS%2Ctext%3A2nd%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))))\n\n"
        "\n 2. Below is Another example search url with filters --  company headcount 201-500, seniority level CXO, Current Job Title Chief Executive Officer," 
        "Geography United States, Connection 1st-degree connections, and Recently Posted on LinkedIn: \n"
        "https://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4390717732%2CdoLogHistory%3Atrue)%2C"
        "filters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AREGION%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AF%2Ctext%3A1st%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APOSTED_ON_LINKEDIN%2Cvalues%3AList((id%3ARPOL%2CselectionType%3AINCLUDED)))))&viewAllFilters=true\n"
        "\n3. Below is example to Exclude people who have viewed your profile recently or messaged recently: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)"
        "%2Cfilters%3AList((type%3ALEAD_INTERACTIONS%2Cvalues%3AList((id%3ALIVP%2Ctext%3AViewed%2520profile%2CselectionType%3AEXCLUDED)"
        "%2C(id%3ALIMP%2Ctext%3AMessaged%2CselectionType%3AEXCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))))"
        "\n 4. Below is example to exclude people who are in your saved leads or accounts list: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3A"
        "List((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))%2C"
        "(type%3ASAVED_LEADS_AND_ACCOUNTS%2Cvalues%3AList((id%3ASL%2Ctext%3AAll%2520my%2520saved%2520leads%2CselectionType%3AEXCLUDED)%2C"
        "(id%3ASA%2Ctext%3AAll%2520my%2520saved%2520accounts%2CselectionType%3AEXCLUDED)))))"
        "\n 5. Below is example to include people with whom you have shared experiences or is past collegue: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2C"
        "filters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))%2C"
        "(type%3AWITH_SHARED_EXPERIENCES%2Cvalues%3AList((id%3ACOMM%2Ctext%3AShared%2520experiences%2CselectionType%3AINCLUDED)))%2C"
        "(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AS%2Ctext%3A2nd%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APAST_COLLEAGUE%2Cvalues%3AList((id%3APCOLL%2CselectionType%3AINCLUDED)))))"
        "\n 6. Below is example to track leads who viewed your profile recently or followed your company page: \n"
        "https://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AVIEWED_YOUR_PROFILE%2Cvalues%3AList((id%3AVYP%2Ctext%3AViewed%2520your%2520profile%2520recently%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFOLLOWS_YOUR_COMPANY%2Cvalues%3AList((id%3ACF%2CselectionType%3AINCLUDED)))))&viewAllFilters=true"
        "\n 7. Below is example Of somer personal filters like name school industry that can be used: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)"
        "%2Cfilters%3AList((type%3AREGION%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A6%2Ctext%3ATechnology%252C%2520Information%2520and%2520Internet%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_OF_EXPERIENCE%2Cvalues%3AList((id%3A4%2Ctext%3A6%2520to%252010%2520years%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASCHOOL%2Cvalues%3AList((id%3A1792%2Ctext%3AStanford%2520University%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFIRST_NAME%2Cvalues%3AList((text%3AJohn%2CselectionType%3AINCLUDED)))%2C(type%3ALAST_NAME%2Cvalues%3A"
        "List((text%3ADoe%2CselectionType%3AINCLUDED)))%2C(type%3AGROUP%2Cvalues%3AList((id%3A5119103%2Ctext%3AMobile%2520Integration%2520Cloud%2520Services%2CselectionType%3AINCLUDED)))))viewAllFilters=true"
        "\n 8. Example of some role related filters you can use like job title, seniority level, years at current company: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters"
        "%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFUNCTION%2Cvalues%3AList((id%3A8%2Ctext%3AEngineering%2CselectionType%3AINCLUDED)%2C(id%3A25%2Ctext%3ASales%2CselectionType%3AINCLUDED)"
        "%2C(id%3A15%2Ctext%3AMarketing%2CselectionType%3AINCLUDED)))%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A120%2Ctext%3ASenior%2CselectionType%3AINCLUDED)"
        "%2C(id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)%2C(id%3A110%2Ctext%3AEntry%2520Level%2CselectionType%3AEXCLUDED)))"
        "%2C(type%3APAST_TITLE%2Cvalues%3AList((id%3A5%2Ctext%3ADirector%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_AT_CURRENT_COMPANY%2Cvalues%3AList((id%3A3%2Ctext%3A3%2520to%25205%2520years%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_IN_CURRENT_POSITION%2Cvalues%3AList((id%3A3%2Ctext%3A3%2520to%25205%2520years%2CselectionType%3AINCLUDED)))))"
        "\n 9. Example of some lead company related filters you can use like company headcount, company name, previous company etc: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3Ac"
        "List((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A136%2Ctext%3AVice%2520President%2520of%2520Sales%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A5289249%2Ctext%3AArangoDB%2CselectionType%3AINCLUDED%2Cparent%3A(id%3A0))))"
        "%2C(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AC%2Ctext%3A11-50%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APAST_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A828370%2Ctext%3ANeo4j%2CselectionType%3AINCLUDED%2Cparent%3A(id%3A0))))"
        "%2C(type%3ACOMPANY_TYPE%2Cvalues%3AList((id%3AP%2Ctext%3APrivately%2520Held%2CselectionType%3AINCLUDED)%2C(id%3AC%2Ctext%3APublic%2520Company%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))))"
    )
    user_prompt = f"""
    {system_message}
    The user wants to build a Sales Navigator people-search URL for LinkedIn. 
    They have described the desired filters in plain English as follows:

    "{english_description}"

    The supported filters are described below (for your reference):

    {supported_filters_explanation}
    
    Few examples of queries for search URL are as follows:
    {few_examples_of_queries}
    {example_query}

    Double check to make sure its in LinkedIn Sales Navigator URL format for query parameters.
    Please return ONLY the resulting URL. 
    Output is in valid JSON format.
    """

    response, status = await get_structured_output_internal(user_prompt, SalesNavQuery, tool_config=tool_config)
    if status != 'SUCCESS':
        raise Exception("Error in generating the email response.")
    return response.model_dump()