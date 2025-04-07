import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
APP_NAME = "AI Personal Email Assistant"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///emails.db")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 5))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 10))

# Email settings
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail")  # gmail, imap
GMAIL_API_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels"
]
CREDENTIALS_DIR = os.getenv("CREDENTIALS_DIR", "credentials")
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "config/credentials.json")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/auth/callback")

# LLM settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, huggingface
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "gpt2")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 500))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Search settings
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "google")  # google, bing
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")
BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")

# Slack settings
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_DEFAULT_CHANNEL = os.getenv("SLACK_DEFAULT_CHANNEL", "general")

# Calendar settings
CALENDAR_INTEGRATION_ENABLED = os.getenv("CALENDAR_INTEGRATION_ENABLED", "True").lower() == "true"
CALENDAR_API_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Email parsing settings
MAX_EMAIL_FETCH = int(os.getenv("MAX_EMAIL_FETCH", 50))
STORE_ATTACHMENTS = os.getenv("STORE_ATTACHMENTS", "False").lower() == "true"
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "attachments")

# Security settings
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-this-in-production")
TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES", 60))
REQUIRE_CONFIRMATION = os.getenv("REQUIRE_CONFIRMATION", "True").lower() == "true"
