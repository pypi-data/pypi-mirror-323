"""
This module provides a set of functions to enrich lead and organization information
using various enrichment tools such as Apollo or ProxyCurl. It also allows
extraction and validation of domains from user-provided links or company websites.
"""

from typing import Any, Dict, List, Optional

import tldextract

from dhisana.utils.apollo_tools import enrich_user_info_with_apollo
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.domain_parser import get_domain_from_website, is_excluded_domain
from dhisana.utils.proxy_curl_tools import (
    enrich_user_info_with_proxy_curl,
)
from dhisana.utils.serpapi_search_tools import (
    find_company_linkedin_url_with_google_search,
    find_user_linkedin_url_google,
    get_company_domain_from_google_search,
)

# The enrichment tools that are permissible for usage.
ALLOWED_ENRICHMENT_TOOLS = ["apollo", "proxycurl", "zoominfo"]

# A map from tool name to the corresponding function that will enrich user info.
USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP = {
    "apollo": enrich_user_info_with_apollo,
    "proxycurl": enrich_user_info_with_proxy_curl,
}




@assistant_tool
async def enrich_lead_information(
    user_properties: Dict[str, Any],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Enrich lead information including company details and LinkedIn URL.
    Steps performed:
      1) Enrich organization information (primary domain, LinkedIn URL, website).
      2) Attempt to fix/find user LinkedIn URL if not present.
      3) Enrich with additional provider data and validate matches (e.g., Apollo).

    :param user_properties: Dictionary containing user/lead details to be enriched.
    :param use_strict_check: Whether to use strict matching in certain search functions.
    :param tool_config: Optional list of tool configuration dicts (e.g., [{"name": "apollo"}, ...]).
    :return: Enriched user_properties dictionary.
    """
    # Make a clone to avoid modifying the original data.
    cloned_properties = dict(user_properties)
    
    # 1) Enrich user info by finding the LinkedIn URL if not present using Google search.
    cloned_properties = await enrich_user_info(
        input_properties=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )

    # 3) Enrich with provider information (Apollo, ZoomInfo, etc.).
    cloned_properties = await enrich_with_provider(cloned_properties, tool_config)

    # 3) Update the organization's domain and website based on the data found.
    await set_organization_domain(
        row=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )
    return cloned_properties


async def enrich_user_info(
    input_properties: Dict[str, Any],
    use_strict_check: bool,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Attempt to find or fix a user's LinkedIn URL using name, title, location, and company information.

    :param input_properties: Dictionary containing user/lead details.
    :param use_strict_check: Whether to use strict matching during searches.
    :param tool_config: Optional list of tool configurations dicts.
    :return: Updated dictionary with user LinkedIn URL if found.
    """
    user_linkedin_url = (input_properties.get("user_linkedin_url") or "").strip()
    input_properties["linkedin_url_match"] = False

    # If the user's LinkedIn URL is missing, attempt to search for it.
    if not user_linkedin_url:
        full_name = (input_properties.get("full_name") or "").strip()
        if not full_name:
            first_name = (input_properties.get("first_name", "") or "").strip()
            last_name = (input_properties.get("last_name", "") or "").strip()
            full_name = f"{first_name} {last_name}".strip()

        title = input_properties.get("job_title", "") or ""
        location = input_properties.get("lead_location", "") or ""
        org_name = (input_properties.get("organization_name", "") or "").strip()
        if full_name and org_name:
            user_linkedin_url = await find_user_linkedin_url_google(
                user_name=full_name,
                user_title=title,
                user_location=location,
                user_company=org_name,
                use_strict_check=use_strict_check,
                tool_config=tool_config,
            )
            input_properties["user_linkedin_url"] = user_linkedin_url

    return input_properties


async def enrich_with_provider(
    cloned_properties: Dict[str, Any],
    tool_config: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Enrich user/lead data using one of the allowed provider tools (e.g., Apollo, ZoomInfo).
    The tool_config should specify which tool(s) to use.

    :param cloned_properties: Dictionary containing user/lead details to be enriched.
    :param tool_config: List of tool configuration dicts, e.g. [{"name": "apollo"}, ...].
    :return: The updated dictionary after enrichment.
    :raises ValueError: If no tool_config is provided or no suitable enrichment tool is found.
    """
    if not tool_config:
        raise ValueError("No tool configuration found.")

    chosen_tool_func = None
    # Find the first suitable tool from the provided config
    for item in tool_config:
        name = item.get("name")
        if name in USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP and name in ALLOWED_ENRICHMENT_TOOLS:
            chosen_tool_func = USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP[name]
            break

    if not chosen_tool_func:
        raise ValueError("No suitable email validation tool found in tool_config.")

    return await chosen_tool_func(cloned_properties, tool_config)





async def enrich_organization_info_from_name(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Given a dictionary (treated like a CSV row) containing 'organization_name',
    'company_linkedin_url', and 'website' keys, enrich the row only if the
    domain and website are currently empty.

    :param row: Dictionary representing a lead or company record.
    :param use_strict_check: Whether to use strict matching for searches.
    :param tool_config: Optional list of tool configuration dicts.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    linkedin_url_key = "company_linkedin_url"
    website_key = "website"

    org_name = (row.get(org_name_key) or "").strip()
    if org_name.lower() in ["none", "freelance"]:
        # If 'organization_name' is just "none" or "freelance," treat it as empty.
        row[org_name_key] = ""
        org_name = ""

    # If no organization name, no point continuing.
    if not org_name:
        return

    # Skip if domain or website is already present.
    if row.get(org_domain_key) or row.get(website_key):
        return

    linkedin_url = row.get(linkedin_url_key, "").strip()
    if not linkedin_url:
        # TODO: If location detail is available, pass it to the search function.
        linkedin_url = await find_company_linkedin_url_with_google_search(
            org_name,
            company_location="US",
            use_strict_check=use_strict_check,
            tool_config=tool_config,
        )

    if linkedin_url:
        row[linkedin_url_key] = linkedin_url
        # Attempt to set the organization's domain and website using the provided info.
        await set_organization_domain(row, use_strict_check, tool_config)
    else:
        row[org_domain_key] = ""


async def set_organization_domain(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Update the row with a 'primary_domain_of_organization' based on 'website' or
    search results if the domain is absent.

    :param row: Dictionary representing a lead or company record.
    :param use_strict_check: Whether to use strict matching for searches.
    :param tool_config: Optional list of tool configuration dicts.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    website_key = "website"

    existing_domain = (row.get(org_domain_key) or "").strip()
    if not existing_domain:
        org_name = (row.get(org_name_key) or "").strip()
        company_website = (row.get(website_key) or "").strip()
        extracted_domain = ""

        # If we already have a website, try extracting its domain.
        if company_website:
            extracted_domain = get_domain_from_website(company_website)
            # If the domain is excluded (social links, aggregator, etc.), wipe it.
            if extracted_domain and is_excluded_domain(extracted_domain):
                extracted_domain = ""
                company_website = ""

        # If we couldn't extract the domain from the website, and strict check is disabled,
        # try searching for the domain using the org name.
        if not extracted_domain and not use_strict_check and org_name:
            extracted_domain = await get_company_domain_from_google_search(
                org_name,
                "US",
                tool_config=tool_config,
            )

        row[org_domain_key] = extracted_domain or ""
        row[website_key] = company_website or ""
