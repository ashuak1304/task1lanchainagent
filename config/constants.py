"""
Constants for the AI Personal Email Assistant
"""

# Application constants
APP_NAME = "AI Personal Email Assistant"
VERSION = "0.1.0"

# Email related constants
EMAIL_BATCH_SIZE = 50
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB
SUPPORTED_ATTACHMENT_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
]

# LLM related constants
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7
PROMPT_TEMPLATES = {
    'email_summary': "Summarize the following email:\n\n{email_content}\n\nSummary:",
    'email_reply': "Generate a reply to the following email:\n\n{email_content}\n\nReply:",
    'action_items': "Extract action items from the following email:\n\n{email_content}\n\nAction items:",
    'event_extraction': "Extract event details from the following email:\n\n{email_content}\n\nEvent details (date, time, location, description):",
    'search_query': "Generate a search query based on this email question:\n\n{email_content}\n\nSearch query:"
}

# Database constants
DB_SCHEMA_VERSION = "1.0"
EMAIL_TABLE = "emails"
THREAD_TABLE = "threads"
USER_TABLE = "users"
ATTACHMENT_TABLE = "attachments"

# API endpoints
GMAIL_API_BASE = "https://www.googleapis.com/gmail/v1"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"
SLACK_API_BASE = "https://slack.com/api"

# Error messages
ERROR_MESSAGES = {
    'auth_failed': "Authentication failed. Please check your credentials.",
    'email_not_found': "Email not found.",
    'api_error': "API error occurred: {error}",
    'db_error': "Database error: {error}",
    'invalid_request': "Invalid request: {error}",
    'llm_error': "Error processing with language model: {error}",
    'integration_error': "Integration error with {service}: {error}"
}

# Status codes
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_PENDING = "pending"

# Integration constants
SLACK_MESSAGE_MAX_LENGTH = 3000
CALENDAR_DEFAULT_REMINDER_MINUTES = 10
SEARCH_RESULT_LIMIT = 5

# UI constants
UI_DATE_FORMAT = "%Y-%m-%d"
UI_TIME_FORMAT = "%H:%M:%S"
UI_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
