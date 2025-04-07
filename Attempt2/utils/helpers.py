# utils/helpers.py

import re
import uuid
from datetime import datetime
from typing import Optional, List
import html
from dateutil import parser

def extract_email_address(email_string: str) -> str:
    """
    Extract email address from a string like 'John Doe <john.doe@example.com>'
    
    Args:
        email_string: String containing an email address
        
    Returns:
        The extracted email address or the original string if no email is found
    """
    pattern = r'[\w\.-]+@[\w\.-]+'
    match = re.search(pattern, email_string)
    if match:
        return match.group(0)
    return email_string

def clean_html(html_content: str) -> str:
    """
    Remove HTML tags from content and decode HTML entities.
    
    Args:
        html_content: String containing HTML
        
    Returns:
        Plain text with HTML tags removed and entities decoded
    """
    # First unescape HTML entities
    text = html.unescape(html_content)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)

def generate_unique_id() -> str:
    """
    Generate a unique ID using UUID.
    
    Returns:
        A unique string ID
    """
    return str(uuid.uuid4())

def parse_date_string(date_string: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_string: String containing a date
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return parser.parse(date_string)
    except:
        return None

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text that may contain URLs
        
    Returns:
        List of extracted URLs
    """
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
