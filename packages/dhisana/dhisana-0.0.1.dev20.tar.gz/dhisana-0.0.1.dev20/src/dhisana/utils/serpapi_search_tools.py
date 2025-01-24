import json
import os
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import urllib
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.web_download_parse_tools import fetch_html_content, get_html_content_from_url

# SERP API tools helps with online google serach. This is better than google customer serach. 
# Provide this as tool to assist in searching for information online.

def get_serp_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the SERPAPI_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The SERPAPI_KEY access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    if tool_config:
        serpapi_config = next(
            (item for item in tool_config if item.get("name") == "serpapi"), None
        )
        if serpapi_config:
            config_map = {
                item["name"]: item["value"]
                for item in serpapi_config.get("configuration", [])
                if item
            }
            SERPAPI_KEY = config_map.get("apiKey")
        else:
            SERPAPI_KEY = None
    else:
        SERPAPI_KEY = None

    SERPAPI_KEY = SERPAPI_KEY or os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY access token not found in tool_config or environment variable")
    return SERPAPI_KEY


@assistant_tool
async def search_google(
    query: str,
    number_of_results: int = 10,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search Google using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return. Default is 10.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    
    cached_response = retrieve_output("search_google_serp", query)
    if cached_response is not None:
        return cached_response

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('organic_results', [])]
                cached_response = cache_output("search_google_serp", query, serialized_results)
                return serialized_results
    except Exception as e:
        return {'error': str(e)}

@assistant_tool
async def search_google_maps(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search Google Maps using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_maps"
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('local_results', [])]
                return serialized_results
    except Exception as e:
        return {'error': str(e)}

@assistant_tool
async def search_google_news(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search Google News using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_news"
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('news_results', [])]
                return serialized_results
    except Exception as e:
        return {'error': str(e)}
    

@assistant_tool
async def search_job_postings(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search for job postings using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_jobs"
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('jobs_results', [])]
                return serialized_results
    except Exception as e:
        return {'error': str(e)}

@assistant_tool
async def search_google_images(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search Google Images using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_images"
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('images_results', [])]
                return serialized_results
    except Exception as e:
        return {'error': str(e)}

@assistant_tool
async def search_google_videos(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search Google Videos using SERP API and return the results as an array of serialized JSON strings.
    Parameters:
    - **query** (*str*): The search query.
    - **number_of_results** (*int*): The number of results to return.
    """
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_videos"
    }

    url = "https://serpapi.com/search"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}
                
                # Serialize each result to JSON string
                serialized_results = [json.dumps(item) for item in result.get('video_results', [])]
                return serialized_results
    except Exception as e:
        return {'error': str(e)}
    
    
    
@assistant_tool
async def get_company_domain_from_google_search(
    company_name: str,
    location: str = None,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Tries to find the company domain from the company name using Google search.

    Args:
        company_name (str): The name of the company to search for.

    Returns:
        str: The domain of the company's official website if found, otherwise an empty string.
    """
    company_name_no_spaces = company_name.replace(" ", "")
    
    if not company_name_no_spaces or company_name.lower() in ["none", "freelance"]:
        return ""
    
    # Search for the company name on Google with the query "official website"
    exclude_company_names = ["linkedin", "wikipedia", "facebook", "instagram", "twitter", "youtube", "netflix", "zoominfo", "reditt"]
    exclusions = ' '.join([f"-site:*.{site}.com" for site in exclude_company_names])
    exclusions = ''
    query = f"\"{company_name}\" official website {exclusions}"
    if location:
        query = f"\"{company_name}\" official website, {location}  {exclusions}"
    result = await search_google(query, 1, tool_config=tool_config)
    
    # Retry search with relaxed contraint if list is empty
    if not isinstance(result, list) or len(result) == 0:
        query = f"{company_name} official website {exclusions}"
        result = await search_google(query, 1)
        
    if not isinstance(result, list) or len(result) == 0:
        return ''
   
    exclude_compan_names = ["linkedin", "wikipedia", "facebook", "instagram", "twitter", "youtube", "netflix"]
    if any(exclude_compan_name in company_name.lower() for exclude_compan_name in exclude_compan_names):
        return ""
    
    try:
        # Parse the JSON string result
        result_json = json.loads(result[0])
    except (json.JSONDecodeError, IndexError):
        return ''
    
    # Get the link from the first result
    link = result_json.get('link', '')

    # If the link is empty, return an empty string
    if not link:
        return ''

    # Parse the URL to get the domain part
    parsed_url = urlparse(link)
    domain = parsed_url.netloc

    # Remove 'www.' if it's present at the start of the domain
    if domain.startswith('www.'):
        domain = domain[4:]

    # List of domains to exclude
    excluded_domains = ["linkedin.com", 
                        "wikipedia.org", "usa.gov", 
                        "facebook.com", "instagram.com", 
                        "twitter.com", 
                        "x.com",
                        "google.com",
                        "youtube.com",
                        "netflix.com",
                        "freelance.com", "zoominfo.com", "reditt.com"]
    
    # Convert both domain and excluded domains to lowercase for case-insensitive comparison
    domain_lower = domain.lower()
    excluded_domains_lower = [d.lower() for d in excluded_domains]
    
    # Check if the domain or any of its subdomains are in the excluded list
    if any(domain_lower == d or domain_lower.endswith(f".{d}") for d in excluded_domains_lower):
        return ""

    # Return the domain
    return domain


@assistant_tool
async def get_signal_strength(
    domain_to_search: str,
    keywords: List[str],
    in_title: List[str] = [],
    not_in_title: List[str] = [],
    negative_keywords: List[str] = [],
    tool_config: Optional[List[Dict]] = None
) -> int:
    """
    Find how strong a match for the keywords in search is.

    Args:
        domain_to_search (str): The domain to search inside.
        keywords (List[str]): The keywords to search for.
        in_title (List[str]): Keywords that must appear in the title.
        not_in_title (List[str]): Keywords that must not appear in the title.
        negative_keywords (List[str]): Keywords to exclude from results.

    Returns:
        int: A strength score on a scale of 0 to 5.
    """
    query = ""
    if domain_to_search:
        query = f"site:{domain_to_search} "
    
    for keyword in keywords:
        query += f"\"{keyword}\" "
    
    for keyword in in_title:
        query += f'intitle:"{keyword}" '
    
    for keyword in not_in_title:
        query += f'-intitle:"{keyword}" '
    
    for keyword in negative_keywords:
        query += f'-"{keyword}" '
            
    if not query.strip():
        return 0
    
    # Search for the keywords on Google with the query
    results = await search_google(query.strip(), 5, tool_config=tool_config)
    
    # Check if the result is empty or not a list
    if not isinstance(results, list) or len(results) == 0:
        return 0

    score = 0
    try:
        for result in results:
            result_json = json.loads(result)
            # If search result contains all keywords, increment the score
            if all(keyword.lower() in result_json.get('snippet', '').lower() for keyword in keywords):
                print("Found a match: ", result_json.get('snippet', ''))
                score += 1
            if score == 5:
                break
    except (json.JSONDecodeError, KeyError):
        return 0    

    return score

def extract_user_linkedin_page(url: str) -> str:
    """
    Extracts and returns the user page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    # Normalize the domain to www.linkedin.com
    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    
    # Match and extract the company page segment
    match = re.match(r"https://www.linkedin.com/in/([\w\-]+)", normalized_url)
    if match:
        # Construct the cleaned URL
        page = f"https://www.linkedin.com/in/{match.group(1)}"
        return page
    
    # If no valid company page is found, return an empty string or appropriate error message
    return ""

@assistant_tool
async def find_user_linkedin_url_google(
    user_name: str,
    user_title: str,
    user_location: str,
    user_company: str,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their name, title, location, and company.

    Args:
        user_name (str): The name of the user.
        user_title (str): The title of the user.
        user_location (str): The location of the user.
        user_company (str): The company of the user.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    if use_strict_check:
        queries = [
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_title}" "{user_company}" intitle:"{user_name}"',
        ]
    else:  
        queries = [
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_title}" "{user_company}" intitle:"{user_name}"',
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_company}" intitle:"{user_name}"',
            f'site:linkedin.com/in "{user_name}", {user_location} intitle:"{user_name}"',
            f'site:linkedin.com/in "{user_name}" intitle:"{user_name}"'
        ]

    for query in queries:
        if not query.strip():
            continue
        
        # Search for the keywords on Google with the query
        results = await search_google(query.strip(), 1, tool_config=tool_config)
        
        # Check if the result is empty or not a list
        if not isinstance(results, list) or len(results) == 0:
            continue

        try:
            # Parse the JSON string result
            result_json = json.loads(results[0])
        except (json.JSONDecodeError, IndexError):
            continue
        
        # Get the link from the first result
        link = result_json.get('link', '')

        # If the link is empty, continue to the next query
        if not link:
            continue

        # Parse the URL to get the domain part
        parsed_url = urlparse(link)
        
        # Check if the URL is in the linkedin.com/in format of a people profile
        if 'linkedin.com/in' in parsed_url.netloc + parsed_url.path:
            link = extract_user_linkedin_page(link)
            return link

    # Return an empty string if no valid link is found
    return ''

@assistant_tool
async def find_user_linkedin_url_by_job_title_google(
    user_title: str,
    user_location: str,
    user_company: str,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their job_title, location, and company.

    Args:
        user_title (str): The title of the user.
        user_location (str): The location of the user.
        user_company (str): The company of the user.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    queries = [
        f'site:linkedin.com/in "{user_company}" "{user_title}" "{user_location}"  intitle:"{user_company}"',
        f'site:linkedin.com/in  "{user_company}" {user_title} {user_location}',
    ]

    for query in queries:
        if not query.strip():
            continue
        
        # Search for the keywords on Google with the query
        results = await search_google(query.strip(), 1, tool_config=tool_config)
        
        # Check if the result is empty or not a list
        if not isinstance(results, list) or len(results) == 0:
            continue

        try:
            # Parse the JSON string result
            result_json = json.loads(results[0])
        except (json.JSONDecodeError, IndexError):
            continue
        
        # Get the link from the first result
        link = result_json.get('link', '')

        # If the link is empty, continue to the next query
        if not link:
            continue

        # Parse the URL to get the domain part
        parsed_url = urlparse(link)
        
        # Check if the URL is in the linkedin.com/in format of a people profile
        if 'linkedin.com/in' in parsed_url.netloc + parsed_url.path:
            link = extract_user_linkedin_page(link)
            return link

    # Return an empty string if no valid link is found
    return ''

def extract_company_page(url: str) -> str:
    """
    Extracts and returns the company page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    # Normalize the domain to www.linkedin.com
    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    
    # Match and extract the company page segment
    match = re.match(r"https://www.linkedin.com/company/([\w\-]+)", normalized_url)
    if match:
        # Construct the cleaned URL
        company_page = f"https://www.linkedin.com/company/{match.group(1)}"
        return company_page
    
    # If no valid company page is found, return an empty string or appropriate error message
    return ""


@assistant_tool
async def find_company_linkedin_url_with_google_search(
    company_name: str,
    company_location: Optional[str] = None,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> str:
    """
    Find the LinkedIn URL for a company based on its name and optional location using Google search.

    Args:
        company_name (str): The name of the company.
        company_location (str, optional): The location of the company.

    Returns:
        str: The LinkedIn URL if found, otherwise an empty string.
    """
    if use_strict_check:
        queries = [
            f'site:linkedin.com/company "{company_name}" {company_location}',
        ]
    else:
        if company_location:
            queries = [
                f'site:linkedin.com/company "{company_name}" {company_location}',
                f'site:linkedin.com/company "{company_name}"',
                f'site:linkedin.com/company {company_name} {company_location}',
            ]
        else:
            queries = [
                    f'site:linkedin.com/company "{company_name}"', 
                    f'site:linkedin.com/company {company_name}'
                    ]

    for query in queries:
        if not query.strip():
            continue

        # Search for the company on Google with the query
        results = await search_google(query.strip(), 1, tool_config=tool_config)

        # Check if the result is empty or not a list
        if not isinstance(results, list) or len(results) == 0:
            continue

        try:
            # Parse the JSON string result
            result_json = json.loads(results[0])
        except (json.JSONDecodeError, IndexError):
            continue

        # Get the link from the first result
        link = result_json.get('link', '')

        # If the link is empty, continue to the next query
        if not link:
            continue

        # Parse the URL to get the domain part
        parsed_url = urlparse(link)

        # Check if the URL is in the linkedin.com/company format
        if 'linkedin.com/company' in parsed_url.netloc + parsed_url.path:
            link = extract_company_page(link)
            return link

    # Return an empty string if no valid link is found
    return ''


async def get_external_links(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    external_links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('http') and not href.startswith(url):
                            external_links.append(href)
                    return external_links
                else:
                    print(f"Error: HTTP {response.status}")
                    return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

async def get_resolved_linkedin_links(url):
    content = await fetch_html_content(url)
    linkedin_links = re.findall(r'https://www\.linkedin\.com/company/[^\s]+', content)
    return list(set(linkedin_links))

@assistant_tool
async def get_company_website_from_linkedin_url(linkedin_url):
    if not linkedin_url:
        return ""
    links = await get_external_links(linkedin_url)
    for link in links:
        if 'trk=about_website' in link:
            parsed_link = urllib.parse.urlparse(link)
            query_params = urllib.parse.parse_qs(parsed_link.query)
            if 'url' in query_params:
                encoded_url = query_params['url'][0]
                company_website = urllib.parse.unquote(encoded_url)
                return company_website
    return ""


@assistant_tool
async def find_job_postings_google_search(
    company_name: str,
    keywords_check: List[str],
    company_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,  
) -> List[str]:
    """
    Find job postings on LinkedIn for a given company using Google Search.

    Args:
        company_name (str): The name of the company.
        company_linkedin_url (Optional[str]): The LinkedIn URL of the company.
        keywords_check (List[str]): A list of keywords to include in the search.

    Returns:
        List[str]: A list of job posting links.
    """
    keywords_list = [kw.strip().lower() for kw in keywords_check]
    
    # Combine all keywords into a single query
    keywords_str = ' '.join(f'"{kw}"' for kw in keywords_list)
    query = f'site:linkedin.com/jobs "{company_name}" {keywords_str}'
    queries = [query]
    
    job_posting_links = []

    for query in queries:
        if not query.strip():
            continue

        # Search for job postings on Google with the query
        results = await search_google(query.strip(), 1, tool_config=tool_config)

        if not isinstance(results, list) or len(results) == 0:
            continue

        # For each result, fetch the page and process
        for result_item in results:
            try:
                result_json = json.loads(result_item)
            except json.JSONDecodeError:
                continue

            link = result_json.get('link', '')

            if not link:
                continue

            # Fetch the page content
            try:
                page_content = await get_html_content_from_url(link)
                # Parse the page content with BeautifulSoup
                soup = BeautifulSoup(page_content, 'html.parser')
            except Exception:
                continue

            # Extract all hrefs from the page
            page_links = [a.get('href') for a in soup.find_all('a', href=True)]

            # Check if company_linkedin_url and 'public_jobs_topcard-org-name' are in the page links
            company_match = False
            if company_linkedin_url:
                for page_link in page_links:
                    if (page_link and company_linkedin_url in page_link and
                        'public_jobs_topcard-org-name' in page_link):
                        company_match = True
                        break

            # Check if any of the keywords are in the page text
            keywords_found = False
            text = soup.get_text().lower()
            for kw in keywords_list:
                if kw in text:
                    keywords_found = True
                    break

            # If both conditions are true, add the job posting link
            if company_match and keywords_found:
                job_posting_links.append(link)

    return job_posting_links