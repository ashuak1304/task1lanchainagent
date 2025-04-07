import unittest
from unittest.mock import patch, MagicMock
import os
import json
import requests
from services.search_service import SearchService
from services.slack_service import SlackService
from services.calendar_service import CalendarService

class TestIntegrations(unittest.TestCase):
    """Test cases for external integrations"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.search_service = SearchService()
        self.slack_service = SlackService()
        self.calendar_service = CalendarService()
        
        # Sample user ID for testing
        self.user_id = "test_user_123"
    
    @patch('services.search_service.requests.get')
    def test_google_search(self, mock_get):
        """Test Google search integration"""
        # Mock the response from Google Custom Search API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Test Result 1',
                    'link': 'https://example.com/result1',
                    'snippet': 'This is the first test result'
                },
                {
                    'title': 'Test Result 2',
                    'link': 'https://example.com/result2',
                    'snippet': 'This is the second test result'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the method
        results = self.search_service.search_web('test query')
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Result 1')
        self.assertEqual(results[0]['link'], 'https://example.com/result1')
        self.assertEqual(results[0]['snippet'], 'This is the first test result')
        self.assertEqual(results[0]['source'], 'Google')
    
    @patch('services.search_service.requests.get')
    def test_bing_search(self, mock_get):
        """Test Bing search integration"""
        # Set search engine to Bing
        self.search_service.search_engine = 'bing'
        
        # Mock the response from Bing Web Search API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'webPages': {
                'value': [
                    {
                        'name': 'Test Result 1',
                        'url': 'https://example.com/result1',
                        'snippet': 'This is the first test result'
                    },
                    {
                        'name': 'Test Result 2',
                        'url': 'https://example.com/result2',
                        'snippet': 'This is the second test result'
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Call the method
        results = self.search_service.search_web('test query')
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Result 1')
        self.assertEqual(results[0]['link'], 'https://example.com/result1')
        self.assertEqual(results[0]['snippet'], 'This is the first test result')
        self.assertEqual(results[0]['source'], 'Bing')
    
    @patch('slack_sdk.WebClient')
    def test_slack_send_message(self, mock_web_client):
        """Test sending a message to Slack"""
        # Mock the Slack client
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client
        
        # Set up the Slack service
        self.slack_service.client = mock_client
        self.slack_service.default_channel = 'test-channel'
        
        # Call the method
        result = self.slack_service.send_message('Test message')
        
        # Assertions
        mock_client.chat_postMessage.assert_called_once_with(
            channel='test-channel',
            text='Test message'
        )
        self.assertTrue(result)
    
    @patch('slack_sdk.WebClient')
    def test_slack_send_email_notification(self, mock_web_client):
        """Test sending an email notification to Slack"""
        # Mock the Slack client
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client
        
        # Set up the Slack service
        self.slack_service.client = mock_client
        self.slack_service.default_channel = 'test-channel'
        
        # Create a mock email
        mock_email = MagicMock()
        mock_email.subject = 'Test Subject'
        mock_email.sender = 'sender@example.com'
        mock_email.received_at.strftime.return_value = '2025-04-06 10:00'
        mock_email.body_text = 'This is a test email body'
        
        # Call the method
        result = self.slack_service.send_email_notification(mock_email)
        
        # Assertions
        mock_client.chat_postMessage.assert_called_once()
        call_args = mock_client.chat_postMessage.call_args[1]
        self.assertEqual(call_args['channel'], 'test-channel')
        self.assertIn('blocks', call_args)
        self.assertTrue(result)
    
    @patch('googleapiclient.discovery.build')
    def test_calendar_create_event(self, mock_build):
        """Test creating a calendar event"""
        # Mock the Calendar service
        mock_calendar_service = MagicMock()
        mock_build.return_value = mock_calendar_service
        
        # Mock the events().insert() method
        mock_insert = MagicMock()
        mock_calendar_service.events.return_value.insert.return_value = mock_insert
        mock_insert.execute.return_value = {'id': 'event123'}
        
        # Initialize the calendar service with the mock
        self.calendar_service.calendar_service = mock_calendar_service
        
        # Event details
        event_details = {
            'summary': 'Test Meeting',
            'location': 'Conference Room',
            'description': 'Discussing project progress',
            'start': {
                'dateTime': '2025-04-07T14:00:00',
                'timeZone': 'Asia/Kolkata'
            },
            'end': {
                'dateTime': '2025-04-07T15:00:00',
                'timeZone': 'Asia/Kolkata'
            }
        }
        
        # Call the method
        success, event_id = self.calendar_service.create_event(self.user_id, event_details)
        
        # Assertions
        mock_calendar_service.events.return_value.insert.assert_called_once_with(
            calendarId='primary',
            body=event_details
        )
        self.assertTrue(success)
        self.assertEqual(event_id, 'event123')
    
    def test_format_search_results(self):
        """Test formatting search results for inclusion in email replies"""
        # Sample search results
        results = [
            {
                'title': 'Test Result 1',
                'link': 'https://example.com/result1',
                'snippet': 'This is the first test result',
                'source': 'Google'
            },
            {
                'title': 'Test Result 2',
                'link': 'https://example.com/result2',
                'snippet': 'This is the second test result',
                'source': 'Google'
            }
        ]
        
        # Call the method
        formatted = self.search_service.format_search_results(results)
        
        # Assertions
        self.assertIn("Here's what I found on the web:", formatted)
        self.assertIn("1. Test Result 1", formatted)
        self.assertIn("https://example.com/result1", formatted)
        self.assertIn("This is the first test result", formatted)
        self.assertIn("2. Test Result 2", formatted)

if __name__ == '__main__':
    unittest.main()
