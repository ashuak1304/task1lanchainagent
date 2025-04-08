ai-personal-email-assistant
![Screenshot 2025-04-07 211058](https://github.com/user-attachments/assets/5b644cf8-e59b-4824-9873-ff52bdfb60c0)


Overview The AI Personal Email Assistant is a Python-based application that uses cutting-edge AI technologies to help manage your emails efficiently. It integrates Gmail, Slack, Google Calendar, and web search capabilities to provide an all-in-one solution for email management, response generation, meeting scheduling, and notifications.

Features Gmail Integration: Fetch and parse emails from your inbox.

Response Generation: Use AI (Hugging Face Transformers) to analyze emails and generate professional responses.

Meeting Scheduling: Extract meeting details from emails and schedule events in Google Calendar.

Slack Notifications: Send notifications about important emails or meetings to Slack.

Web Search Integration: Enhance responses with relevant information from the web using Google Custom Search API.

Streamlit Interface: A user-friendly UI to interact with the assistant.

Technologies Used Python

Streamlit: For the user interface

Hugging Face Transformers: For AI-powered email analysis and response generation

Google APIs:

Gmail API

Google Calendar API

Google Custom Search API

Slack SDK: For Slack integration

SQLite: For storing email data and conversation history

Installation Prerequisites Python 3.9 or higher installed on your system.

A Google Cloud project with Gmail API, Calendar API, and Custom Search API enabled.

Slack App created with appropriate permissions.

Steps Clone the repository:

bash git clone https://github.com/yourusername/ai-email-assistant.git cd ai-email-assistant Create a virtual environment:

bash python -m venv myvenv Activate the virtual environment:

On Windows:

bash myvenv\Scripts\activate On macOS/Linux:

bash source myvenv/bin/activate Install dependencies:

bash pip install -r requirements.txt Set up environment variables:

Create a .env file in the project root with the following content:

text

Gmail API
GMAIL_CREDENTIALS_FILE=credentials.json GMAIL_TOKEN_FILE=token.json

Database
DATABASE_URL=sqlite:///data/database.db

Slack
SLACK_API_TOKEN=xoxb-your-slack-token SLACK_CHANNEL=email-notifications

Calendar API
CALENDAR_CREDENTIALS_FILE=calendar_credentials.json CALENDAR_TOKEN_FILE=calendar_token.json

LLM Configuration (Hugging Face Transformers)
LLM_MODEL_ID=microsoft/Phi-3-mini-4k-instruct USE_4BIT_QUANTIZATION=True MAX_NEW_TOKENS=512 TEMPERATURE=0.7

Web Search API (Google Custom Search)
SEARCH_API_KEY=your-google-search-api-key SEARCH_ENGINE_ID=your-search-engine-id Download the required credentials files:

credentials.json: From Google Cloud Console for Gmail API.

calendar_credentials.json: From Google Cloud Console for Calendar API.

Run the application:

bash streamlit run app.py Usage Inbox Management View your Gmail inbox directly in the Streamlit interface.

Select an email to analyze its content and intent using AI.

Response Generation Generate professional responses using Hugging Face Transformers.

Edit responses directly in the UI before sending.

Meeting Scheduling Automatically extract meeting details from emails.

Schedule events in Google Calendar with one click.

Slack Notifications Send email summaries or meeting requests to Slack channels for quick collaboration.
