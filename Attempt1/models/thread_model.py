from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Thread(Base):
    """Model representing an email thread/conversation"""
    __tablename__ = 'threads'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Thread metadata
    subject = Column(String(255), nullable=True)
    snippet = Column(Text, nullable=True)
    participants = Column(Text, nullable=True)  # JSON array of email addresses
    
    # Status information
    is_important = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emails = relationship("Email", back_populates="thread")
    user = relationship("User", back_populates="threads")
    
    # LLM-generated context
    context_summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)  # JSON array of action items
    
    def __repr__(self):
        return f"<Thread(id={self.id}, subject='{self.subject}')>"
    
    @property
    def email_count(self):
        """Get the number of emails in this thread"""
        return len(self.emails) if self.emails else 0
    
    @property
    def latest_email(self):
        """Get the most recent email in the thread"""
        if not self.emails:
            return None
        return sorted(self.emails, key=lambda e: e.received_at, reverse=True)[0]
    
    def update_context_summary(self, summary):
        """Update the LLM-generated context summary"""
        self.context_summary = summary
        
    def update_action_items(self, items):
        """Update the action items extracted by LLM"""
        import json
        self.action_items = json.dumps(items)
        
    def get_action_items(self):
        """Get the action items as a Python list"""
        if not self.action_items:
            return []
        import json
        return json.loads(self.action_items)
    
    def add_participant(self, email_address):
        """Add a participant to the thread"""
        import json
        participants = []
        if self.participants:
            participants = json.loads(self.participants)
        
        if email_address not in participants:
            participants.append(email_address)
            self.participants = json.dumps(participants)
    
    def get_participants(self):
        """Get the list of participants"""
        if not self.participants:
            return []
        import json
        return json.loads(self.participants)
    
    @classmethod
    def create_from_gmail(cls, gmail_thread, user_id):
        """Create a Thread instance from a Gmail API thread object"""
        thread = cls(
            thread_id=gmail_thread['id'],
            user_id=user_id,
            snippet=gmail_thread.get('snippet', ''),
        )
        
        # Extract subject from the first message if available
        if 'messages' in gmail_thread and len(gmail_thread['messages']) > 0:
            first_message = gmail_thread['messages'][0]
            headers = {header['name']: header['value'] for header in 
                      first_message.get('payload', {}).get('headers', [])}
            thread.subject = headers.get('Subject', '')
        
        return thread
