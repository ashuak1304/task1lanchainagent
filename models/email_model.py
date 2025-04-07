from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Email(Base):
    """Model representing an email in the system"""
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    thread_id = Column(String(255), ForeignKey('threads.thread_id'), nullable=True)
    
    # Email metadata
    sender = Column(String(255), nullable=False)
    sender_name = Column(String(255), nullable=True)
    recipient = Column(String(255), nullable=False)
    cc = Column(Text, nullable=True)
    bcc = Column(Text, nullable=True)
    subject = Column(String(255), nullable=True)
    
    # Email content
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    # Status flags
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    attachments = relationship("Attachment", back_populates="email")
    thread = relationship("Thread", back_populates="emails")
    user = relationship("User", back_populates="emails")
    
    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject}', sender='{self.sender}')>"
    
    @classmethod
    def create_from_gmail(cls, gmail_message, user_id):
        """Create an Email instance from a Gmail API message object"""
        headers = {header['name']: header['value'] for header in gmail_message.get('payload', {}).get('headers', [])}
        
        email = cls(
            message_id=gmail_message['id'],
            user_id=user_id,
            thread_id=gmail_message.get('threadId'),
            sender=headers.get('From', ''),
            sender_name=cls._extract_sender_name(headers.get('From', '')),
            recipient=headers.get('To', ''),
            cc=headers.get('Cc', ''),
            bcc=headers.get('Bcc', ''),
            subject=headers.get('Subject', ''),
            received_at=cls._parse_date(headers.get('Date')),
            is_read=not gmail_message.get('labelIds', {}).get('UNREAD', False)
        )
        
        # Parse body content
        if 'payload' in gmail_message and 'body' in gmail_message['payload']:
            if gmail_message['payload']['mimeType'] == 'text/plain':
                email.body_text = cls._decode_body(gmail_message['payload']['body'])
            elif gmail_message['payload']['mimeType'] == 'text/html':
                email.body_html = cls._decode_body(gmail_message['payload']['body'])
            elif gmail_message['payload']['mimeType'] == 'multipart/alternative':
                for part in gmail_message['payload'].get('parts', []):
                    if part['mimeType'] == 'text/plain':
                        email.body_text = cls._decode_body(part['body'])
                    elif part['mimeType'] == 'text/html':
                        email.body_html = cls._decode_body(part['body'])
        
        return email
    
    @staticmethod
    def _extract_sender_name(from_header):
        """Extract sender name from From header"""
        if '<' in from_header and '>' in from_header:
            return from_header.split('<')[0].strip(' "\'')
        return None
    
    @staticmethod
    def _parse_date(date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Handle various date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.utcnow()
    
    @staticmethod
    def _decode_body(body_data):
        """Decode email body content"""
        if 'data' in body_data:
            import base64
            return base64.urlsafe_b64decode(body_data['data']).decode('utf-8')
        return None


class Attachment(Base):
    """Model representing an email attachment"""
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    content_id = Column(String(255), nullable=True)
    size = Column(Integer, nullable=False, default=0)
    
    # Store attachment data or path to file
    data = Column(Text, nullable=True)  # For small attachments
    file_path = Column(String(255), nullable=True)  # For large attachments stored on disk
    
    # Relationship
    email = relationship("Email", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', size={self.size})>"


class Thread(Base):
    """Model representing an email thread/conversation"""
    __tablename__ = 'threads'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    subject = Column(String(255), nullable=True)
    snippet = Column(Text, nullable=True)
    
    # Most recent activity
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emails = relationship("Email", back_populates="thread")
    user = relationship("User", back_populates="threads")
    
    def __repr__(self):
        return f"<Thread(id={self.id}, subject='{self.subject}')>"
