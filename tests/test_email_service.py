import unittest
from unittest.mock import patch, MagicMock
import os
import json
from services.email_service import EmailService
from models.email_model import Email, Attachment
from models.thread_model import Thread

class TestEmailService(unittest.TestCase):
    """Test cases for the EmailService class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.email_service = EmailService()
        
        # Mock user credentials
        self.user_id = "test_user_123"
        
        # Sample email data
        self.sample_email_data = {
            'id': 'msg123',
            'threadId': 'thread123',
            'labelIds': ['INBOX'],
            'snippet': 'This is a test email',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Subject', 'value': 'Test Email Subject'},
                    {'name': 'Date', 'value': 'Mon, 3 Apr 2025 10:00:00 +0000'}
                ],
                'mimeType': 'text/plain',
                'body': {
                    'data': 'VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keQ=='  # "This is a test email body" in base64
                }
            }
        }
    
    @patch('services.email_service.load_credentials')
    @patch('services.email_service.build')
    def test_initialize_for_user(self, mock_build, mock_load_credentials):
        """Test initializing Gmail API service for a user"""
        # Mock the credentials
        mock_credentials = MagicMock()
        mock_load_credentials.return_value = mock_credentials
        
        # Mock the Gmail service
        mock_gmail_service = MagicMock()
        mock_build.return_value = mock_gmail_service
        
        # Call the method
        result = self.email_service.initialize_for_user(self.user_id)
        
        # Assertions
        mock_load_credentials.assert_called_once_with(self.user_id)
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_credentials)
        self.assertEqual(result, mock_gmail_service)
        self.assertEqual(self.email_service.gmail_service, mock_gmail_service)
    
    @patch('services.email_service.load_credentials')
    @patch('services.email_service.build')
    def test_get_inbox(self, mock_build, mock_load_credentials):
        """Test fetching emails from inbox"""
        # Mock the Gmail service and its methods
        mock_gmail_service = MagicMock()
        mock_build.return_value = mock_gmail_service
        
        # Mock the messages.list method
        mock_list = MagicMock()
        mock_gmail_service.users().messages().list.return_value = mock_list
        mock_list.execute.return_value = {
            'messages': [
                {'id': 'msg123', 'threadId': 'thread123'},
                {'id': 'msg456', 'threadId': 'thread456'}
            ]
        }
        
        # Mock the get_email method
        self.email_service.get_email = MagicMock()
        mock_email1 = MagicMock()
        mock_email2 = MagicMock()
        self.email_service.get_email.side_effect = [mock_email1, mock_email2]
        
        # Call the method
        result = self.email_service.get_inbox(self.user_id, max_results=2)
        
        # Assertions
        mock_gmail_service.users().messages().list.assert_called_once_with(
            userId='me',
            labelIds=['INBOX'],
            maxResults=2
        )
        self.assertEqual(self.email_service.get_email.call_count, 2)
        self.assertEqual(result, [mock_email1, mock_email2])
    
    @patch('services.email_service.load_credentials')
    @patch('services.email_service.build')
    def test_get_email(self, mock_build, mock_load_credentials):
        """Test fetching a specific email"""
        # Mock the Gmail service and its methods
        mock_gmail_service = MagicMock()
        mock_build.return_value = mock_gmail_service
        
        # Mock the messages.get method
        mock_get = MagicMock()
        mock_gmail_service.users().messages().get.return_value = mock_get
        mock_get.execute.return_value = self.sample_email_data
        
        # Mock Email.create_from_gmail
        with patch('models.email_model.Email.create_from_gmail') as mock_create:
            mock_email = MagicMock()
            mock_email.id = 1
            mock_email.attachments = []
            mock_create.return_value = mock_email
            
            # Call the method
            result = self.email_service.get_email(self.user_id, 'msg123')
            
            # Assertions
            mock_gmail_service.users().messages().get.assert_called_once_with(
                userId='me',
                id='msg123',
                format='full'
            )
            mock_create.assert_called_once_with(self.sample_email_data, self.user_id)
            self.assertEqual(result, mock_email)
    
    @patch('services.email_service.load_credentials')
    @patch('services.email_service.build')
    @patch('services.email_service.MIMEMultipart')
    @patch('services.email_service.MIMEText')
    @patch('services.email_service.base64')
    def test_send_email(self, mock_base64, mock_mime_text, mock_mime_multipart, mock_build, mock_load_credentials):
        """Test sending an email"""
        # Mock the Gmail service and its methods
        mock_gmail_service = MagicMock()
        mock_build.return_value = mock_gmail_service
        
        # Mock MIMEMultipart
        mock_message = MagicMock()
        mock_mime_multipart.return_value = mock_message
        
        # Mock base64 encoding
        mock_base64.urlsafe_b64encode.return_value = b'encoded_message'
        mock_base64.urlsafe_b64encode.return_value.decode.return_value = 'encoded_message'
        
        # Mock the messages.send method
        mock_send = MagicMock()
        mock_gmail_service.users().messages().send.return_value = mock_send
        mock_send.execute.return_value = {'id': 'sent123'}
        
        # Call the method
        result = self.email_service.send_email(
            self.user_id,
            'recipient@example.com',
            'Test Subject',
            'Test Body',
            html='<p>Test HTML Body</p>'
        )
        
        # Assertions
        mock_mime_multipart.assert_called_once_with('alternative')
        self.assertEqual(mock_message['to'], 'recipient@example.com')
        self.assertEqual(mock_message['subject'], 'Test Subject')
        self.assertEqual(mock_mime_text.call_count, 2)  # Once for plain text, once for HTML
        mock_gmail_service.users().messages().send.assert_called_once_with(
            userId='me',
            body={'raw': 'encoded_message'}
        )
        self.assertEqual(result, {'id': 'sent123'})
    
    @patch('services.email_service.load_credentials')
    @patch('services.email_service.build')
    def test_search_emails(self, mock_build, mock_load_credentials):
        """Test searching emails"""
        # Mock the Gmail service and its methods
        mock_gmail_service = MagicMock()
        mock_build.return_value = mock_gmail_service
        
        # Mock the messages.list method
        mock_list = MagicMock()
        mock_gmail_service.users().messages().list.return_value = mock_list
        mock_list.execute.return_value = {
            'messages': [
                {'id': 'msg123', 'threadId': 'thread123'},
                {'id': 'msg456', 'threadId': 'thread456'}
            ]
        }
        
        # Mock the get_email method
        self.email_service.get_email = MagicMock()
        mock_email1 = MagicMock()
        mock_email2 = MagicMock()
        self.email_service.get_email.side_effect = [mock_email1, mock_email2]
        
        # Call the method
        result = self.email_service.search_emails(self.user_id, 'test query')
        
        # Assertions
        mock_gmail_service.users().messages().list.assert_called_once_with(
            userId='me',
            q='test query',
            maxResults=20
        )
        self.assertEqual(self.email_service.get_email.call_count, 2)
        self.assertEqual(result, [mock_email1, mock_email2])

if __name__ == '__main__':
    unittest.main()
