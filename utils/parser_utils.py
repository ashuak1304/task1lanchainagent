import re
import base64
import email
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup
from datetime import datetime

def parse_email_content(raw_email):
    """
    Parse raw email content into structured format
    
    Args:
        raw_email: Raw email content (string or bytes)
        
    Returns:
        dict: Parsed email with headers and content
    """
    if isinstance(raw_email, str):
        raw_email = raw_email.encode('utf-8')
    
    # Parse the email
    parser = BytesParser(policy=default)
    parsed_email = parser.parsebytes(raw_email)
    
    # Extract headers
    headers = {}
    for key in parsed_email.keys():
        headers[key.lower()] = parsed_email[key]
    
    # Extract body content
    body_text = None
    body_html = None
    attachments = []
    
    # Process the email parts
    if parsed_email.is_multipart():
        for part in parsed_email.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Handle attachments
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    attachment_data = part.get_payload(decode=True)
                    attachments.append({
                        "filename": filename,
                        "content_type": content_type,
                        "data": attachment_data,
                        "size": len(attachment_data)
                    })
            # Handle text parts
            elif content_type == "text/plain" and not body_text:
                body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
            # Handle HTML parts
            elif content_type == "text/html" and not body_html:
                body_html = part.get_payload(decode=True).decode('utf-8', errors='replace')
    else:
        # Handle non-multipart emails
        content_type = parsed_email.get_content_type()
        if content_type == "text/plain":
            body_text = parsed_email.get_payload(decode=True).decode('utf-8', errors='replace')
        elif content_type == "text/html":
            body_html = parsed_email.get_payload(decode=True).decode('utf-8', errors='replace')
    
    # Create structured email object
    structured_email = {
        "headers": headers,
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "cc": headers.get("cc", ""),
        "date": parse_date(headers.get("date", "")),
        "body_text": body_text,
        "body_html": body_html,
        "attachments": attachments
    }
    
    return structured_email

def extract_email_addresses(text):
    """
    Extract email addresses from text
    
    Args:
        text: Text containing email addresses
        
    Returns:
        list: List of extracted email addresses
    """
    if not text:
        return []
    
    # Regular expression for email addresses
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(pattern, text)

def extract_names_from_email_header(from_header):
    """
    Extract sender name from From header
    
    Args:
        from_header: From header string
        
    Returns:
        tuple: (name, email_address)
    """
    if not from_header:
        return (None, None)
    
    # Pattern for "Name <email@example.com>" format
    pattern = r'(.*?)\s*<(.+?)>'
    match = re.search(pattern, from_header)
    
    if match:
        name = match.group(1).strip(' "\'')
        email_address = match.group(2)
        return (name, email_address)
    else:
        # If no name found, the whole string is likely just an email
        return (None, from_header.strip())

def html_to_text(html_content):
    """
    Convert HTML content to plain text
    
    Args:
        html_content: HTML content string
        
    Returns:
        str: Plain text version of the HTML
    """
    if not html_content:
        return ""
    
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading/trailing space
    lines = (line.strip() for line in text.splitlines())
    
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def parse_date(date_string):
    """
    Parse date string to datetime object
    
    Args:
        date_string: Date string from email header
        
    Returns:
        datetime: Parsed datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    try:
        # Try to parse using email.utils
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_string)
    except:
        # Fallback to common formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822
            '%d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S',
            '%d %b %Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except:
                continue
        
        return None

def decode_base64(data):
    """
    Decode base64 data
    
    Args:
        data: Base64 encoded string
        
    Returns:
        bytes: Decoded data
    """
    # Add padding if needed
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    
    try:
        return base64.b64decode(data)
    except:
        try:
            return base64.urlsafe_b64decode(data)
        except:
            return None

def extract_urls_from_text(text):
    """
    Extract URLs from text
    
    Args:
        text: Text containing URLs
        
    Returns:
        list: List of extracted URLs
    """
    if not text:
        return []
    
    # Regular expression for URLs
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(pattern, text)

def extract_potential_event_details(text):
    """
    Extract potential event details from text
    
    Args:
        text: Email body text
        
    Returns:
        dict: Extracted event details or None if no event detected
    """
    if not text:
        return None
    
    # Look for date patterns
    date_patterns = [
        r'(?:on|date:?)\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s*,?\s*\d{4})?)',
        r'(\d{1,2}/\d{1,2}/\d{2,4})',
        r'(\d{4}-\d{1,2}-\d{1,2})'
    ]
    
    # Look for time patterns
    time_patterns = [
        r'(?:at|time:?)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
        r'(\d{1,2}(?::\d{2})?\s*(?:to|-)\s*\d{1,2}(?::\d{2})?\s*(?:am|pm))'
    ]
    
    # Look for location patterns
    location_patterns = [
        r'(?:at|in|location:?)\s*([^,.]+(?:conference room|office|building|center|centre))',
        r'location:?\s*([^,.]+)'
    ]
    
    # Extract potential event details
    date_match = None
    for pattern in date_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            date_match = matches.group(1)
            break
    
    time_match = None
    for pattern in time_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            time_match = matches.group(1)
            break
    
    location_match = None
    for pattern in location_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            location_match = matches.group(1)
            break
    
    # If we found at least a date or time, consider it a potential event
    if date_match or time_match:
        return {
            "date": date_match,
            "time": time_match,
            "location": location_match,
            "description": extract_event_description(text)
        }
    
    return None

def extract_event_description(text):
    """
    Extract a potential event description from text
    
    Args:
        text: Email body text
        
    Returns:
        str: Potential event description
    """
    # Look for meeting/event description patterns
    patterns = [
        r'(?:meeting|call|event|discussion) (?:about|regarding|on|for)\s*([^,.]+)',
        r'(?:invitation|invite):\s*([^,.]+)',
        r'(?:subject|topic|agenda):\s*([^,.]+)'
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return matches.group(1).strip()
    
    return None
