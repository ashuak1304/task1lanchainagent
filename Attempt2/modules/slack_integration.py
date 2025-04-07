import os
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import SLACK_API_TOKEN, SLACK_CHANNEL

class SlackIntegration:
    def __init__(self):
        self.client = WebClient(token=SLACK_API_TOKEN)
        self.default_channel = SLACK_CHANNEL
    
    def send_message(self, message: str, channel: Optional[str] = None) -> bool:
        """Send a message to a Slack channel."""
        try:
            # Use default channel if none specified
            target_channel = channel or self.default_channel
            
            # Send the message
            response = self.client.chat_postMessage(
                channel=target_channel,
                text=message
            )
            
            print(f"Message sent to Slack channel {target_channel}")
            return True
        
        except SlackApiError as e:
            print(f"Error sending message to Slack: {e.response['error']}")
            return False
    
    def send_email_notification(self, email_data: Dict[str, Any]) -> bool:
        """Send a notification about a new email to Slack."""
        try:
            # Format the message
            message = f"""
*New Email Received*
*From:* {email_data.get('sender', 'Unknown')}
*Subject:* {email_data.get('subject', 'No Subject')}
*Summary:* {email_data.get('summary', 'No summary available')}

_Received at: {email_data.get('timestamp', 'Unknown time')}_
            """
            
            # Send the message
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Email"
                                },
                                "value": email_data.get('id', '')
                            }
                        ]
                    }
                ]
            )
            
            print(f"Email notification sent to Slack channel {self.default_channel}")
            return True
        
        except SlackApiError as e:
            print(f"Error sending email notification to Slack: {e.response['error']}")
            return False
    
    def send_meeting_notification(self, meeting_details: Dict[str, Any], email_id: str) -> bool:
        """Send a notification about a meeting request to Slack."""
        try:
            # Format the message
            message = f"""
*Meeting Request*
*Title:* {meeting_details.get('Title', 'Untitled Meeting')}
*Date:* {meeting_details.get('Date', 'Not specified')}
*Time:* {meeting_details.get('Time', 'Not specified')}
*Duration:* {meeting_details.get('Duration', 'Not specified')} minutes
*Participants:* {meeting_details.get('Participants', 'Not specified')}
*Location:* {meeting_details.get('Location', 'Not specified')}

_From email: {email_id}_
            """
            
            # Send the message
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Accept Meeting"
                                },
                                "style": "primary",
                                "value": f"accept_{email_id}"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Decline Meeting"
                                },
                                "style": "danger",
                                "value": f"decline_{email_id}"
                            }
                        ]
                    }
                ]
            )
            
            print(f"Meeting notification sent to Slack channel {self.default_channel}")
            return True
        
        except SlackApiError as e:
            print(f"Error sending meeting notification to Slack: {e.response['error']}")
            return False
    
    def send_response_preview(self, email_id: str, draft_response: str) -> bool:
        """Send a preview of an email response to Slack for approval."""
        try:
            # Format the message
            message = f"""
*Draft Email Response*
{draft_response}

_For email ID: {email_id}_
            """
            
            # Send the message
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Send Response"
                                },
                                "style": "primary",
                                "value": f"send_{email_id}"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Edit Response"
                                },
                                "value": f"edit_{email_id}"
                            }
                        ]
                    }
                ]
            )
            
            print(f"Response preview sent to Slack channel {self.default_channel}")
            return True
        
        except SlackApiError as e:
            print(f"Error sending response preview to Slack: {e.response['error']}")
            return False
