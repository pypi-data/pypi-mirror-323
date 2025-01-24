import re
import unicodedata

from dhisana.utils.assistant_tool_tag import assistant_tool

@assistant_tool
def normalize_company_name(company_name: str) -> str:
    """
    Normalize a company name by removing special characters, truncating after specific delimiters,
    removing common legal suffixes, and limiting the length to 64 characters.

    Parameters:
    - company_name (str): The original company name.

    Returns:
    - str: The normalized company name.
    """
    if not company_name:
        return ""

    # Step 1: Convert to lowercase
    normalized_name = company_name.lower()

    # Step 2: Remove content after specific delimiters
    normalized_name = re.split(r'[|,]', normalized_name)[0]

    # Step 3: Remove special characters and punctuation
    normalized_name = re.sub(r'[^\w\s]', '', normalized_name)

    # Step 4: Normalize whitespace
    normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()

    # Step 5: Remove common suffixes
    suffixes = r'\b(inc|llc|ltd|plc|llp|cic|unlimited|pvt ltd|opc pvt ltd|producer company limited|co|company|corporation|gmbh|plc|pvt|private|limited)\b'
    normalized_name = re.sub(suffixes, '', normalized_name)

    # Step 6: Remove accents
    normalized_name = ''.join(
        c for c in unicodedata.normalize('NFD', normalized_name)
        if unicodedata.category(c) != 'Mn'
    )

    # Step 7: Trim to a maximum length of 64 characters
    normalized_name = normalized_name[:64].strip()

    return normalized_name