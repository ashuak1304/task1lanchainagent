import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.auth_utils import load_credentials
from models.email_model import Email, Attachment
from models.thread_model import Thread

class EmailService:
    """Service for handling email operations with Gmail API"""
    
    def __init__(self):
        """Initialize the email service"""
        self.gmail_service = None
    
    def initialize_for_user(self, user_id):
        """Initialize Gmail API service for a specific user"""
        credentials = load_credentials(user_id)
        if not credentials:
            raise ValueError("No credentials found for user")
        
        self.gmail_service = build('gmail', 'v1', credentials=credentials)
        return self.gmail_service
    
    def get_inbox(self, user_id, max_results=50):
        """Fetch emails from user's inbox"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        # Get messages from inbox
        results = self.gmail_service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            email = self.get_email(user_id, message['id'])
            if email:
                emails.append(email)
        
        return emails
    
    def get_email(self, user_id, message_id):
        """Fetch a specific email by ID"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Convert Gmail message to Email model
            email = Email.create_from_gmail(message, user_id)
            
            # Process attachments if any
            if 'payload' in message and 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename') and part['filename'].strip():
                        attachment = self._process_attachment(part, email.id)
                        if attachment:
                            email.attachments.append(attachment)
            
            return email
            
        except Exception as e:
            print(f"Error fetching email {message_id}: {str(e)}")
            return None
    
    def _process_attachment(self, part, email_id):
        """Process and save email attachment"""
        if not part.get('body') or not part.get('body').get('attachmentId'):
            return None
        
        try:
            attachment = Attachment(
                email_id=email_id,
                filename=part.get('filename', 'unnamed'),
                content_type=part.get('mimeType', 'application/octet-stream'),
                content_id=part.get('headers', {}).get('Content-ID', None),
                size=int(part.get('body', {}).get('size', 0))
            )
            
            # For small attachments, we could fetch and store them
            # For production, consider storing file paths instead of raw data
            
            return attachment
            
        except Exception as e:
            print(f"Error processing attachment: {str(e)}")
            return None
    
    def send_email(self, user_id, to, subject, body, html=None):
        """Send a new email"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            
            # Plain text version
            message.attach(MIMEText(body, 'plain'))
            
            # HTML version (if provided)
            if html:
                message.attach(MIMEText(html, 'html'))
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send the message
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return sent_message
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return None
    
    def reply_to_email(self, user_id, message_id, body, html=None):
        """Reply to an existing email"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            # Get the original message to extract headers
            original = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'To', 'Message-ID', 'References', 'In-Reply-To']
            ).execute()
            
            headers = {header['name']: header['value'] for header in original['payload']['headers']}
            
            # Create reply message
            message = MIMEMultipart('alternative')
            message['to'] = headers.get('From')
            message['subject'] = f"Re: {headers.get('Subject', '')}"
            
            # Set reply headers
            if 'Message-ID' in headers:
                message['In-Reply-To'] = headers['Message-ID']
                message['References'] = headers.get('References', '') + ' ' + headers['Message-ID']
            
            # Plain text version
            message.attach(MIMEText(body, 'plain'))
            
            # HTML version (if provided)
            if html:
                message.attach(MIMEText(html, 'html'))
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send the message
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            # Mark the original message as replied
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['REPLIED']}
            ).execute()
            
            return sent_message
            
        except Exception as e:
            print(f"Error replying to email: {str(e)}")
            return None
    
    def search_emails(self, user_id, query, max_results=20):
        """Search emails using Gmail query syntax"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email = self.get_email(user_id, message['id'])
                if email:
                    emails.append(email)
            
            return emails
            
        except Exception as e:
            print(f"Error searching emails: {str(e)}")
            return []
    
    def mark_as_read(self, user_id, message_id):
        """Mark an email as read"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as read: {str(e)}")
            return False
    
    def archive_email(self, user_id, message_id):
        """Archive an email (remove from inbox)"""
        if not self.gmail_service:
            self.initialize_for_user(user_id)
        
        try:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error archiving email: {str(e)}")
            return False
