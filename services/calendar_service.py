import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.auth_utils import load_credentials

class CalendarService:
    """Service for handling Google Calendar operations"""
    
    def __init__(self):
        """Initialize the calendar service"""
        self.calendar_service = None
    
    def initialize_for_user(self, user_id):
        """Initialize Google Calendar API service for a specific user"""
        credentials = load_credentials(user_id)
        if not credentials:
            raise ValueError("No credentials found for user")
        
        self.calendar_service = build('calendar', 'v3', credentials=credentials)
        return self.calendar_service
    
    def get_upcoming_events(self, user_id, max_results=10):
        """Get upcoming calendar events for a user"""
        if not self.calendar_service:
            self.initialize_for_user(user_id)
        
        # Get the current time in RFC3339 format
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        try:
            # Call the Calendar API
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except Exception as e:
            print(f"Error getting upcoming events: {str(e)}")
            return []
    
    def create_event(self, user_id, event_details):
        """Create a calendar event"""
        if not self.calendar_service:
            self.initialize_for_user(user_id)
        
        try:
            # Create the event
            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event_details
            ).execute()
            
            return True, event.get('id')
            
        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return False, None
    
    def extract_event_from_email(self, email_body):
        """Extract potential event details from email body"""
        # This is a simplified implementation
        # In a real application, use the LLM service to extract event details
        
        event = {
            'summary': 'Event from Email',
            'location': '',
            'description': 'Automatically created from email',
            'start': {
                'dateTime': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True
            }
        }
        
        # Look for date/time patterns
        # Look for location information
        # Look for event title/description
        
        return event
    
    def get_configuration(self, user_id):
        """Get calendar configuration for a user"""
        # In a real implementation, this would fetch from the database
        return {
            'is_configured': bool(self.calendar_service),
            'primary_calendar': 'primary'
        }
    
    def configure(self, user_id, primary_calendar=None):
        """Configure calendar integration for a user"""
        # In a real implementation, this would store in the database
        return True
    
    def test_connection(self, user_id=None):
        """Test calendar connection"""
        if not self.calendar_service and user_id:
            try:
                self.initialize_for_user(user_id)
            except:
                return False
        
        if not self.calendar_service:
            return False
        
        try:
            # Test API call
            self.calendar_service.calendarList().list(maxResults=1).execute()
            return True
        except:
            return False
