import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SlackService:
    """Service for handling Slack integration operations"""
    
    def __init__(self):
        """Initialize the Slack service"""
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.default_channel = os.getenv('SLACK_DEFAULT_CHANNEL', 'general')
        self.client = None
        
        # Initialize Slack client if token is available
        if self.slack_token:
            self.client = WebClient(token=self.slack_token)
    
    def configure(self, user_id, workspace, channel, token):
        """Configure Slack integration for a user"""
        try:
            # Store configuration in database (implementation depends on your DB setup)
            # For now, we'll just update the instance variables
            self.slack_token = token
            self.default_channel = channel
            self.client = WebClient(token=token)
            
            # Test the connection to verify credentials
            self.client.auth_test()
            
            return True
        except SlackApiError as e:
            print(f"Error configuring Slack: {e.response['error']}")
            return False
    
    def send_message(self, message, channel=None):
        """Send a message to a Slack channel"""
        if not self.client:
            raise ValueError("Slack client not initialized. Configure Slack first.")
        
        # Use default channel if none specified
        channel = channel or self.default_channel
        
        try:
            # Post message to Slack
            response = self.client.chat_postMessage(
                channel=channel,
                text=message
            )
            return True
        except SlackApiError as e:
            print(f"Error sending message to Slack: {e.response['error']}")
            return False
    
    def send_email_notification(self, email, channel=None):
        """Send an email notification to Slack"""
        if not self.client:
            raise ValueError("Slack client not initialized. Configure Slack first.")
        
        # Use default channel if none specified
        channel = channel or self.default_channel
        
        # Format email as a Slack message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New Email: {email.subject}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*From:*\n{email.sender}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Received:*\n{email.received_at.strftime('%Y-%m-%d %H:%M')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Content:*\n{email.body_text[:500]}..."
                }
            }
        ]
        
        try:
            # Post formatted message to Slack
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text=f"New email from {email.sender}: {email.subject}"
            )
            return True
        except SlackApiError as e:
            print(f"Error sending email notification to Slack: {e.response['error']}")
            return False
    
    def get_configuration(self, user_id):
        """Get Slack configuration for a user"""
        # In a real implementation, this would fetch from the database
        # For now, return the current configuration
        return {
            'token': self.slack_token and '***' or None,  # Don't return actual token
            'default_channel': self.default_channel,
            'is_configured': bool(self.client)
        }
    
    def test_connection(self, user_id=None):
        """Test Slack connection"""
        if not self.client:
            return False
        
        try:
            # Test API call
            response = self.client.auth_test()
            return True
        except SlackApiError:
            return False
