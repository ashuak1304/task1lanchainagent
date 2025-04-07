import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API configuration
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/database.db")

# Slack configuration
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "email-notifications")

# Calendar configuration
CALENDAR_CREDENTIALS_FILE = os.getenv("CALENDAR_CREDENTIALS_FILE", "calendar_credentials.json")
CALENDAR_TOKEN_FILE = os.getenv("CALENDAR_TOKEN_FILE", "calendar_token.json")
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# LLM configuration
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "microsoft/Phi-3-mini-4k-instruct")
USE_4BIT_QUANTIZATION = os.getenv("USE_4BIT_QUANTIZATION", "True").lower() == "true"
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Web search configuration
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
