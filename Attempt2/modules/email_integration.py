import os
import base64
import email
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import re

from config import GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, GMAIL_SCOPES
from modules.memory_manager import save_email, save_attachment

class GmailIntegration:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Check if token file exists
        if os.path.exists(GMAIL_TOKEN_FILE):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(GMAIL_TOKEN_FILE).read()), GMAIL_SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(GMAIL_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        # Build the Gmail service
        return build('gmail', 'v1', credentials=creds)
    
    def get_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from Gmail."""
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            email_data = self._parse_email(message['id'])
            if email_data:
                emails.append(email_data)
                
                # Save email to database
                save_email(email_data)
                
                # Save attachments to database
                if email_data.get('attachments'):
                    for attachment in email_data['attachments']:
                        save_attachment(attachment)
        
        return emails
    
    def _parse_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Parse an email from Gmail."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full').execute()
            
            # Get email headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            recipient = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
            
            # Parse date
            timestamp = datetime.now()
            if date_str:
                try:
                    # This is a simplified approach - email dates can be complex
                    timestamp = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                except:
                    pass
            
            # Get email body
            body = self._get_email_body(message['payload'])
            
            # Check for attachments
            attachments = []
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename') and part.get('body') and part['body'].get('attachmentId'):
                        attachment_id = part['body']['attachmentId']
                        attachment = self.service.users().messages().attachments().get(
                            userId='me', messageId=message_id, id=attachment_id).execute()
                        
                        attachments.append({
                            'id': str(uuid.uuid4()),
                            'email_id': message_id,
                            'filename': part['filename'],
                            'content_type': part['mimeType'],
                            'size': len(attachment.get('data', '')),
                            'data': attachment.get('data', '')
                        })
            
            # Create email data dictionary
            email_data = {
                'id': message_id,
                'sender': sender,
                'recipient': recipient,
                'subject': subject,
                'body': body,
                'timestamp': timestamp,
                'thread_id': message.get('threadId', message_id),
                'has_attachment': bool(attachments),
                'attachments': attachments
            }
            
            return email_data
        except Exception as e:
            print(f"Error parsing email {message_id}: {str(e)}")
            return None
    
    def _get_email_body(self, payload) -> str:
        """Extract the email body from the payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                if part['mimeType'] == 'text/html' and part['body'].get('data'):
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    # Simple HTML to text conversion (could use a library like BeautifulSoup for better results)
                    return re.sub('<[^<]+?>', '', html)
                if 'parts' in part:
                    body = self._get_email_body(part)
                    if body:
                        return body
        
        return "No content found"
    
    def send_email(self, to: str, subject: str, body: str, reply_to_message_id: Optional[str] = None) -> bool:
        """Send an email via Gmail."""
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            # Add reply headers if replying to a message
            if reply_to_message_id:
                original_message = self.service.users().messages().get(
                    userId='me', id=reply_to_message_id, format='metadata',
                    metadataHeaders=['Message-ID', 'Subject', 'References', 'In-Reply-To']).execute()
                
                headers = {h['name']: h['value'] for h in original_message['payload']['headers']}
                
                # Set In-Reply-To header
                if 'Message-ID' in headers:
                    message['In-Reply-To'] = headers['Message-ID']
                
                # Set References header
                references = headers.get('References', '')
                if 'Message-ID' in headers:
                    if references:
                        references += ' '
                    references += headers['Message-ID']
                
                if references:
                    message['References'] = references
                
                # Update subject if needed
                if not subject.startswith('Re:') and headers.get('Subject', '').strip():
                    message['subject'] = f"Re: {headers['Subject']}"
            
            # Attach body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create the message
            created_message = {
                'raw': encoded_message
            }
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me', body=created_message).execute()
            
            print(f"Message sent. Message ID: {sent_message['id']}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
            return True
        except Exception as e:
            print(f"Error marking message as read: {str(e)}")
            return False
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails from Gmail."""
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results, q='is:unread').execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            email_data = self._parse_email(message['id'])
            if email_data:
                emails.append(email_data)
        
        return emails
