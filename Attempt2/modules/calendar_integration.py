import os
import datetime
from typing import Dict, Any, List, Optional
import uuid
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

from config import CALENDAR_CREDENTIALS_FILE, CALENDAR_TOKEN_FILE, CALENDAR_SCOPES

class CalendarIntegration:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # Check if token file exists
        if os.path.exists(CALENDAR_TOKEN_FILE):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(CALENDAR_TOKEN_FILE).read()), CALENDAR_SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CALENDAR_CREDENTIALS_FILE, CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(CALENDAR_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        # Build the Calendar service
        return build('calendar', 'v3', credentials=creds)
    
    def create_event(self, event_details: Dict[str, Any]) -> Optional[str]:
        """Create a calendar event from the provided details."""
        try:
            # Format the event
            event = {
                'summary': event_details.get('Title', 'Meeting'),
                'location': event_details.get('Location', ''),
                'description': event_details.get('Description', ''),
                'start': {
                    'dateTime': self._format_datetime(
                        event_details.get('Date', ''), 
                        event_details.get('Time', '')
                    ),
                    'timeZone': 'Asia/Kolkata',  # Default to IST, can be made configurable
                },
                'end': {
                    'dateTime': self._calculate_end_time(
                        event_details.get('Date', ''),
                        event_details.get('Time', ''),
                        event_details.get('Duration', '60')  # Default 60 minutes
                    ),
                    'timeZone': 'Asia/Kolkata',  # Default to IST, can be made configurable
                },
                'attendees': self._parse_attendees(event_details.get('Participants', '')),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},  # 30 minutes before
                    ],
                },
            }
            
            # Create the event
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
            return event.get('id')
        
        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return None
    
    def _format_datetime(self, date_str: str, time_str: str) -> str:
        """Format date and time strings into RFC3339 timestamp."""
        # Handle empty or invalid date/time
        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if not time_str:
            time_str = datetime.datetime.now().strftime('%H:%M')
        
        # Clean up the time string (remove timezone info if present)
        time_str = time_str.split()[0]
        
        # Combine date and time
        dt_str = f"{date_str}T{time_str}:00"
        
        # Validate and return
        try:
            # Parse the datetime to ensure it's valid
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
            return dt.isoformat()
        except ValueError:
            # Return current time if parsing fails
            return datetime.datetime.now().isoformat()
    
    def _calculate_end_time(self, date_str: str, time_str: str, duration_str: str) -> str:
        """Calculate the end time based on start time and duration."""
        # Parse duration to minutes
        try:
            duration_minutes = int(duration_str)
        except (ValueError, TypeError):
            duration_minutes = 60  # Default to 60 minutes
        
        # Get start time
        start_time_str = self._format_datetime(date_str, time_str)
        
        # Parse the start time
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str)
        except ValueError:
            start_time = datetime.datetime.now()
        
        # Calculate end time
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        
        return end_time.isoformat()
    
    def _parse_attendees(self, participants_str: str) -> List[Dict[str, str]]:
        """Parse a comma-separated list of participants into attendee objects."""
        if not participants_str:
            return []
        
        attendees = []
        for participant in participants_str.split(','):
            email = participant.strip()
            if '@' in email:  # Simple validation
                attendees.append({'email': email})
        
        return attendees
    
    def get_available_slots(self, date_str: str, duration_minutes: int = 60) -> List[Dict[str, str]]:
        """Get available time slots for a given date."""
        try:
            # Parse the date
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            
            # Set time boundaries (9 AM to 5 PM)
            time_min = datetime.datetime.combine(date_obj.date(), datetime.time(9, 0))
            time_max = datetime.datetime.combine(date_obj.date(), datetime.time(17, 0))
            
            # Get events for the day
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Find free slots
            free_slots = []
            current_time = time_min
            
            for event in events:
                start = event['start'].get('dateTime')
                if start:
                    start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    
                    # Check if there's enough time for a meeting
                    if (start_time - current_time).total_seconds() / 60 >= duration_minutes:
                        free_slots.append({
                            'start': current_time.strftime('%H:%M'),
                            'end': start_time.strftime('%H:%M')
                        })
                    
                    # Move current time to the end of this event
                    end = event['end'].get('dateTime')
                    if end:
                        current_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            # Check for a slot after the last event
            if (time_max - current_time).total_seconds() / 60 >= duration_minutes:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': time_max.strftime('%H:%M')
                })
            
            return free_slots
        
        except Exception as e:
            print(f"Error getting available slots: {str(e)}")
            return []
    
    def suggest_meeting_times(self, date_str: str, duration_minutes: int = 60, num_suggestions: int = 3) -> List[str]:
        """Suggest meeting times based on calendar availability."""
        available_slots = self.get_available_slots(date_str, duration_minutes)
        
        suggestions = []
        for slot in available_slots[:num_suggestions]:
            suggestions.append(f"{date_str} at {slot['start']}")
        
        return suggestions
