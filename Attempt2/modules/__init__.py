# modules/__init__.py

# Import all module components for easier access
from modules.email_integration import GmailIntegration
from modules.llm_processor import LLMProcessor
from modules.memory_manager import init_db, get_email_by_id, get_emails_by_thread, save_email, save_attachment, save_response, get_all_emails
from modules.slack_integration import SlackIntegration
from modules.search_integration import SearchIntegration
from modules.calendar_integration import CalendarIntegration

# Define what's available when importing from the package
__all__ = [
    'GmailIntegration',
    'LLMProcessor',
    'SlackIntegration',
    'SearchIntegration',
    'CalendarIntegration',
    'init_db',
    'get_email_by_id',
    'get_emails_by_thread',
    'save_email',
    'save_attachment',
    'save_response',
    'get_all_emails'
]
