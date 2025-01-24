import asyncio
import json
import logging
import os
import aiohttp
import backoff
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.domain_parser import get_domain_from_website, is_excluded_domain
from dhisana.utils.serpapi_search_tools import search_google
from dhisana.utils.web_download_parse_tools import get_html_content_from_url
from urllib.parse import urlparse
from urllib.parse import urlparse, urlunparse

def get_proxycurl_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the PROXY_CURL_API_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The PROXY_CURL_API_KEY access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    if tool_config:
        proxy_curl_config = next(
            (item for item in tool_config if item.get("name") == "proxycurl"), None
        )
        if proxy_curl_config:
            config_map = {
                item["name"]: item["value"]
                for item in proxy_curl_config.get("configuration", [])
                if item
            }
            PROXY_CURL_API_KEY = config_map.get("apiKey")
        else:
            PROXY_CURL_API_KEY = None
    else:
        PROXY_CURL_API_KEY = None

    PROXY_CURL_API_KEY = PROXY_CURL_API_KEY or os.getenv("PROXY_CURL_API_KEY")
    if not PROXY_CURL_API_KEY:
        raise ValueError("PROXY_CURL_API_KEY access token not found in tool_config or environment variable")
    return PROXY_CURL_API_KEY

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_person_info_from_proxycurl(
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch a person's details from Proxycurl using LinkedIn URL, email, or phone number.

    Parameters:
    - linkedin_url (str, optional): LinkedIn profile URL of the person.
    - email (str, optional): Email address of the person.
    - phone (str, optional): Phone number of the person.

    Returns:
    - dict: JSON response containing person information.
    """
    API_KEY = get_proxycurl_access_token(tool_config)

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not linkedin_url and not email and not phone:
        return {'error': "At least one of linkedin_url, email, or phone must be provided"}
    
    if linkedin_url:
        cached_response = retrieve_output("enrich_person_info_from_proxycurl", linkedin_url)
        if cached_response is not None:
            return cached_response


    params = {}
    if linkedin_url:
        params['url'] = linkedin_url
    if email:
        params['email'] = email
    if phone:
        params['phone'] = phone

    url = 'https://nubela.co/proxycurl/api/v2/linkedin'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as response:
            if response.status == 200:
                result = await response.json()
                if linkedin_url:
                    cache_output("enrich_person_info_from_proxycurl", linkedin_url, result)
                return result
            elif response.status == 404:
                if linkedin_url:
                    cache_output("enrich_person_info_from_proxycurl", linkedin_url, {'error': "Person not found"})
                return {'error': "Person not found"}
            elif response.status == 429:
                await asyncio.sleep(30)
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                return {'error': await response.text()}


@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def lookup_person_in_proxy_curl_by_name(
    first_name: str,
    last_name: str,
    company_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
):
    if not first_name or not last_name:
        return {'error': "Full name is required"}

    API_KEY = get_proxycurl_access_token(tool_config)
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {
        'first_name': first_name,
        'last_name': last_name,
        'page_size': '1',
    }
    if company_name:
        params['company'] = company_name
    key = f"{first_name} {last_name} {company_name}".strip()
    if key:
        cached_response = retrieve_output("lookup_person_in_proxy_curl_by_name", key)
        if cached_response is not None:
            return cached_response

    url = 'https://nubela.co/proxycurl/api/v2/search/person'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                result = await response.json()
                cache_output("lookup_person_in_proxy_curl_by_name", key, result)
                return result
            elif response.status == 404:
                if key:
                    cache_output("lookup_person_in_proxy_curl_by_name", key, {'error': "Person not found"})
                return {'error': "Person not found"}
            elif response.status == 429:
                logging.warning("Rate limit hit")
                await asyncio.sleep(30)
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                result = await response.json()
                logging.warning(f"lookup_person_in_proxy_by_name error: {result}")
                return {'error': result}

@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_organization_info_from_proxycurl(
    organization_domain: Optional[str] = None,
    organization_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch an organization's details from Proxycurl using either the organization domain or LinkedIn URL.

    Parameters:
    - organization_domain (str, optional): Domain of the organization.
    - organization_linkedin_url (str, optional): LinkedIn URL of the organization.

    Returns:
    - dict: JSON response containing organization information.
    """
    API_KEY = get_proxycurl_access_token(tool_config)

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not organization_domain and not organization_linkedin_url:
        return {'error': "Either organization domain or LinkedIn URL must be provided"}

    if organization_linkedin_url:
        # Standardize LinkedIn URL to 'https://www.linkedin.com/company/<public_identifier>' format
        parsed_url = urlparse(organization_linkedin_url)
        if parsed_url.netloc != 'www.linkedin.com':
            standardized_netloc = 'www.linkedin.com'
            standardized_path = parsed_url.path
            if not standardized_path.startswith('/company/'):
                standardized_path = '/company' + standardized_path
            standardized_url = urlunparse(parsed_url._replace(netloc=standardized_netloc, path=standardized_path))
            if standardized_url and not standardized_url.endswith('/'):
                standardized_url += '/'
        else:
            standardized_url = organization_linkedin_url
            if standardized_url and not standardized_url.endswith('/'):
                standardized_url += '/'

        # Check if LinkedIn URL data is cached
        cached_response = retrieve_output("enrich_organization_info_from_proxycurl", standardized_url)
        if cached_response is not None:
            return cached_response

        # Fetch details using standardized LinkedIn URL
        url = 'https://nubela.co/proxycurl/api/linkedin/company'
        params = {
            'url': standardized_url,
            'categories': 'include',
            'funding_data': 'include',
            'exit_data': 'include',
            'acquisitions': 'include',
            'extra': 'include',
            'use_cache': 'if-present',
            'fallback_to_cache': 'on-error',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    cache_output("enrich_organization_info_from_proxycurl", standardized_url, result)
                    return result
                else:
                    return {'error': await response.text()}

    if organization_domain:
        # Check if domain data is cached
        cached_response = retrieve_output("enrich_organization_info_from_proxycurl", organization_domain)
        if cached_response is not None:
            return cached_response

        # Resolve company URL from domain
        resolve_url = 'https://nubela.co/proxycurl/api/linkedin/company/resolve'
        params = {'domain': organization_domain}

        async with aiohttp.ClientSession() as session:
            async with session.get(resolve_url, headers=HEADERS, params=params) as response:
                if response.status == 200:
                    company_data = await response.json()
                    company_url = company_data.get('url')
                    if company_url:
                        # Standardize the resolved LinkedIn URL
                        parsed_url = urlparse(company_url)
                        if parsed_url.netloc != 'www.linkedin.com':
                            standardized_netloc = 'www.linkedin.com'
                            standardized_path = parsed_url.path
                            if not standardized_path.startswith('/company/'):
                                standardized_path = '/company' + standardized_path
                            standardized_url = urlunparse(parsed_url._replace(netloc=standardized_netloc, path=standardized_path))
                        else:
                            standardized_url = company_url

                        # Fetch company profile using standardized LinkedIn URL
                        profile_url = 'https://nubela.co/proxycurl/api/v2/linkedin/company'
                        async with session.get(profile_url, headers=HEADERS, params={'url': standardized_url}) as profile_response:
                            if profile_response.status == 200:
                                result = await profile_response.json()
                                cache_output("enrich_organization_info_from_proxycurl", organization_domain, result)
                                return result
                            else:
                                return {'error': await profile_response.json()}
                    else:
                        return {'error': 'Company URL not found for the provided domain'}
                elif response.status == 429:
                    await asyncio.sleep(30)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message="Rate limit exceeded",
                        headers=response.headers
                    )
                elif response.status == 404:
                    if organization_domain:
                        cache_output("enrich_organization_info_from_proxycurl", organization_domain, {'error': 'Item not found'})
                    return {'error': "Person not found"}
                else:
                    return {'error': await response.text()}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_job_info_from_proxycurl(
    job_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch a job's details from Proxycurl using the job URL.

    Parameters:
    - job_url (str, optional): URL of the LinkedIn job posting.

    Returns:
    - dict: JSON response containing job information.
    """
    API_KEY = get_proxycurl_access_token(tool_config)

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not job_url:
        return {'error': "Job URL must be provided"}
    
    if job_url:
        cached_response = retrieve_output("enrich_job_info_from_proxycurl", job_url)
        if cached_response is not None:
            return cached_response

    params = {'url': job_url}
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/job'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_endpoint, headers=HEADERS, params=params) as response:
            if response.status == 200:
                result = await response.json()
                if job_url:
                    cache_output("enrich_job_info_from_proxycurl", job_url, result)
                return result
            elif response.status == 429:
                await asyncio.sleep(30)
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            elif response.status == 404:
                if job_url:
                    cache_output("enrich_job_info_from_proxycurl", job_url, {'error': "Job not found"})
                return {'error': "Job not found"}
            else:
                return {'error': await response.text()}

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def search_recent_job_changes(
    job_titles: List[str],
    locations: List[str],
    max_items_to_return: int = 100,
    tool_config: Optional[List[Dict]] = None
) -> List[dict]:
    """
    Search for individuals with specified job titles and locations who have recently changed jobs.

    Parameters:
    - job_titles (List[str]): List of job titles to search for.
    - locations (List[str]): List of locations to search in.
    - max_items_to_return (int, optional): Maximum number of items to return. Defaults to 100.

    Returns:
    - List[dict]: List of individuals matching the criteria.
    """
    
    API_KEY = get_proxycurl_access_token(tool_config)

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }


    url = 'https://nubela.co/proxycurl/api/search/person'
    results = []
    page = 1
    per_page = min(max_items_to_return, 100)

    async with aiohttp.ClientSession() as session:
        while len(results) < max_items_to_return:
            params = {
                'job_title': ','.join(job_titles),
                'location': ','.join(locations),
                'page': page,
                'num_records': per_page
            }
            async with session.get(url, headers=HEADERS, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    people = data.get('persons', [])
                    if not people:
                        break
                    results
 
@assistant_tool
async def find_matching_job_posting_proxy_curl(
    company_name: str,
    keywords_check: List[str],
    optional_keywords: List[str],
    company_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None  
) -> List[str]:
    """
    Find job postings on LinkedIn for a given company using Google Custom Search.
    Double check the same with Proxycurl API.

    Args:
        company_name (str): The name of the company.
        keywords_check (List[str]): A list of keywords to include in the search.
        optinal_keywords (List[str]): A list of optional keywords to include in the search.
        company_linkedin_url (Optional[str]): The LinkedIn URL of the company.

    Returns:
        List[str]: A list of job posting links.
    """
    keywords_list = [kw.strip().lower() for kw in keywords_check]
    job_posting_links = []

    
    # Combine all keywords into a single query
    keywords_str = ' '.join(f'"{kw}"' for kw in keywords_check)
    optional_keywords_str = ' '.join(f'{kw}' for kw in optional_keywords)
    query = f'site:*linkedin.com/jobs/view/ "{company_name}" {keywords_str} {optional_keywords_str}'
    

    # Search for job postings on Google with the query
    results = await search_google(query.strip(), 1)
    if not isinstance(results, list) or len(results) == 0:
        query = f'site:*linkedin.com/jobs/view/ "{company_name}" {keywords_str}'
        # Search for job postings on Google with the query
        results = await search_google(query.strip(), 1, tool_config=tool_config)
        if not isinstance(results, list) or len(results) == 0:
            return job_posting_links
    
        

    # For each result, fetch the page and process
    for result_item in results:
        try:
            result_json = json.loads(result_item)
        except json.JSONDecodeError:
            continue

        link = result_json.get('link', '')

        if not link:
            continue
        
        if "linkedin.com/jobs/view/" in link:
            parsed = urlparse(link)
            new_link = parsed._replace(netloc="www.linkedin.com").geturl()
            link = new_link
        else:
            continue
        
        # Fetch the page content
        try:
            json_result = await enrich_job_info_from_proxycurl(link, tool_config=tool_config)
        except Exception:
            continue

        if not json_result:
            continue

        text = json.dumps(json_result).lower()
        
        if company_linkedin_url and json_result.get('company', {}) and json_result.get('company', {}).get('url', ''):
            result_url = json_result.get('company', {}).get('url', '').lower()
            result_path = urlparse(result_url).path
            company_path = urlparse(company_linkedin_url.lower()).path
            company_match = result_path == company_path
        else:
            company_match = False

        
        keywords_found = any(kw in text for kw in keywords_list)

        # If both conditions are true, add the job posting link
        if company_match and keywords_found:
            job_posting_links.append(link)

    return job_posting_links


async def enrich_user_info_with_proxy_curl(input_user_properties, tool_config):
    linkedin_url = input_user_properties.get("user_linkedin_url", "")
    email = input_user_properties.get("email", "")
    user_data_from_proxycurl = None

    # If linkedin url is present or email is present then lookup by them
    if linkedin_url or email:
        user_data_from_proxycurl = await enrich_person_info_from_proxycurl(
            linkedin_url=linkedin_url,
            email=email,
            tool_config=tool_config
        )
        if user_data_from_proxycurl and linkedin_url:
            input_user_properties["user_linkedin_url"] = linkedin_url
    else:
        # Else lookup by name
        first_name = input_user_properties.get("first_name", "")
        last_name = input_user_properties.get("last_name", "")
        full_name = input_user_properties.get("full_name", "")

        if not first_name or not last_name:
            if full_name:
                name_parts = full_name.split(" ", 1)
                first_name = first_name or name_parts[0]
                last_name = last_name or (name_parts[1] if len(name_parts) > 1 else "")
                
        if not full_name:
            full_name = f"{first_name} {last_name}".strip()
        company = input_user_properties.get("organization_name", "")

        if first_name and last_name:
            # Lookup person by name
            search_result = await lookup_person_in_proxy_curl_by_name(
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                tool_config=tool_config
            )

            results = search_result.get("results", [])
            person_company = ""
            for person in results:
                #Retrive the search result and check if the name and company matches
                linkedin_url = person.get("linkedin_profile_url", "")
                if linkedin_url:
                    data_from_proxycurl = await enrich_person_info_from_proxycurl(
                        linkedin_url=linkedin_url,
                        tool_config=tool_config
                    )
                    if data_from_proxycurl:
                        person_name = data_from_proxycurl.get("name", "").lower()
                        person_first_name = data_from_proxycurl.get("first_name", "").lower()
                        person_last_name = data_from_proxycurl.get("last_name", "").lower()
                        experiences = data_from_proxycurl.get('experiences', [])
                        for exp in experiences:
                            exp_company = exp.get("company", "").lower()
                            if exp_company == company.lower():
                                person_company = exp_company
                                break
                        #If there is match then set the 
                        if (
                            (person_name == full_name.lower() or
                            (person_first_name == first_name.lower() and person_last_name == last_name.lower()))
                            and (not company or person_company == company.lower())
                        ):
                                input_user_properties["user_linkedin_url"] = linkedin_url
                                user_data_from_proxycurl = data_from_proxycurl
                                break
                
                    

    if not user_data_from_proxycurl:
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    person_data = user_data_from_proxycurl

    additional_props = input_user_properties.get("additional_properties") or {}
    additional_props["proxy_curl_person_data"] = json.dumps(person_data)
    input_user_properties["additional_properties"] = additional_props

    if not input_user_properties.get("email", ""):
        input_user_properties["email"] = person_data.get("email", "")
    if not input_user_properties.get("phone", ""):
        input_user_properties["phone"] = person_data.get("contact", {}).get("sanitized_phone", "")

    if person_data.get("full_name"):
        input_user_properties["full_name"] = person_data["full_name"]
    if person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]
    if person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]

    if person_data.get("occupation"):
        input_user_properties["job_title"] = person_data["occupation"]

    if person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]

    if person_data.get("summary") and not input_user_properties.get("summary_about_lead"):
        input_user_properties["summary_about_lead"] = person_data["summary"]

    experiences = person_data.get("experiences", [])
    if experiences and len(experiences) > 0:
        input_user_properties["organization_name"] = experiences[0].get("company", "")
    

    if person_data.get("city") or person_data.get("state"):
        combined = f"{person_data.get('city', '')}, {person_data.get('state', '')}"
        input_user_properties["lead_location"] = combined.strip(", ")
    
    if experiences and len(experiences) > 0:
        company_linkedin_url = experiences[0].get("company_linkedin_profile_url", "")
        if company_linkedin_url:
            input_user_properties["company_linkedin_url"] = company_linkedin_url
            #TODO enrich company information optionally
            # if company_linkedin_url:
            #     organization_data = await enrich_organization_info_from_proxycurl(organization_domain="", organization_linkedin_url=company_linkedin_url, tool_config=tool_config)
            #     if organization_data:
            #         additional_props["proxy_curl_organization_data"] = organization_data
            #         input_user_properties["website"] = organization_data.get("website", "")
                    # if previous_website:
                    #         input_user_properties["previous_company_website"] = previous_website
                    #         extracted_domain = get_domain_from_website(previous_website)
                    #         # If the domain is excluded (social links, aggregator, etc.), wipe it.
                    #         if extracted_domain and not is_excluded_domain(extracted_domain):
                    #             input_user_properties["previous_organization_primary_domain"] = extracted_domain

    if experiences and len(experiences) > 1:
        previous_org = experiences[1]
        previous_company_linkedin_url = previous_org.get("company_linkedin_profile_url", "")
        if previous_company_linkedin_url:
            input_user_properties["previous_company_linkedin_url"] = previous_company_linkedin_url
            input_user_properties["previous_organization_name"] = previous_org.get("company", "")            
            
    first_matched = bool(
        input_user_properties.get("first_name")
        and person_data.get("first_name") == input_user_properties["first_name"]
    )
    last_matched = bool(
        input_user_properties.get("last_name")
        and person_data.get("last_name") == input_user_properties["last_name"]
    )
    if first_matched and last_matched:
        input_user_properties["linkedin_url_match"] = True

    return input_user_properties

