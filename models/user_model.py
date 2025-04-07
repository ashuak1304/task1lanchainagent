from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()

class User(Base):
    """Model representing a user in the system"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    
    # Authentication data
    auth_provider = Column(String(50), default='google')  # google, imap, etc.
    credentials_json = Column(Text, nullable=True)  # Encrypted OAuth credentials
    
    # Integration settings
    slack_config = Column(Text, nullable=True)  # JSON with Slack settings
    calendar_config = Column(Text, nullable=True)  # JSON with Calendar settings
    
    # User preferences
    preferences = Column(Text, nullable=True)  # JSON with user preferences
    
    # Account status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    emails = relationship("Email", back_populates="user")
    threads = relationship("Thread", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def set_credentials(self, credentials):
        """Store OAuth credentials as JSON string"""
        # In a production environment, these should be encrypted
        if hasattr(credentials, 'to_json'):
            self.credentials_json = credentials.to_json()
        else:
            self.credentials_json = json.dumps(credentials)
    
    def get_credentials(self):
        """Retrieve OAuth credentials from JSON string"""
        if not self.credentials_json:
            return None
        
        try:
            from google.oauth2.credentials import Credentials
            return Credentials.from_json(self.credentials_json)
        except:
            return json.loads(self.credentials_json)
    
    def set_slack_config(self, workspace, channel, token):
        """Store Slack configuration"""
        config = {
            'workspace': workspace,
            'default_channel': channel,
            'token': token  # In production, encrypt this
        }
        self.slack_config = json.dumps(config)
    
    def get_slack_config(self):
        """Retrieve Slack configuration"""
        if not self.slack_config:
            return None
        return json.loads(self.slack_config)
    
    def set_calendar_config(self, calendar_id=None, notification_settings=None):
        """Store Calendar configuration"""
        config = {
            'primary_calendar': calendar_id,
            'notifications': notification_settings or {}
        }
        self.calendar_config = json.dumps(config)
    
    def get_calendar_config(self):
        """Retrieve Calendar configuration"""
        if not self.calendar_config:
            return None
        return json.loads(self.calendar_config)
    
    def set_preference(self, key, value):
        """Set a user preference"""
        prefs = {}
        if self.preferences:
            prefs = json.loads(self.preferences)
        
        prefs[key] = value
        self.preferences = json.dumps(prefs)
    
    def get_preference(self, key, default=None):
        """Get a user preference"""
        if not self.preferences:
            return default
        
        prefs = json.loads(self.preferences)
        return prefs.get(key, default)
    
    def get_all_preferences(self):
        """Get all user preferences"""
        if not self.preferences:
            return {}
        return json.loads(self.preferences)
