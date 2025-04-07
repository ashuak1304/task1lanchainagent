import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import DATABASE_URL

# Ensure data directory exists
os.makedirs(os.path.dirname(DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Email(Base):
    __tablename__ = 'emails'
    
    id = Column(String, primary_key=True)
    sender = Column(String)
    recipient = Column(String)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(DateTime)
    thread_id = Column(String)
    has_attachment = Column(Boolean, default=False)
    
    attachments = relationship("Attachment", back_populates="email")
    responses = relationship("Response", back_populates="email")
    
    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "thread_id": self.thread_id,
            "has_attachment": self.has_attachment
        }

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(String, primary_key=True)
    email_id = Column(String, ForeignKey('emails.id'))
    filename = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    data = Column(Text)  # Base64 encoded data
    
    email = relationship("Email", back_populates="attachments")
    
    def to_dict(self):
        return {
            "id": self.id,
            "email_id": self.email_id,
            "filename": self.filename,
            "content_type": self.content_type,
            "size": self.size
        }

class Response(Base):
    __tablename__ = 'responses'
    
    id = Column(String, primary_key=True)
    email_id = Column(String, ForeignKey('emails.id'))
    content = Column(Text)
    timestamp = Column(DateTime)
    sent = Column(Boolean, default=False)
    
    email = relationship("Email", back_populates="responses")
    
    def to_dict(self):
        return {
            "id": self.id,
            "email_id": self.email_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sent": self.sent
        }

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    
    id = Column(String, primary_key=True)
    thread_id = Column(String)
    messages = Column(Text)  # JSON serialized messages
    last_updated = Column(DateTime)
    
    def get_messages(self):
        return json.loads(self.messages) if self.messages else []
    
    def set_messages(self, messages_list):
        self.messages = json.dumps(messages_list)
        self.last_updated = datetime.now()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)

def get_email_by_id(email_id: str) -> Optional[Email]:
    """Retrieve an email by its ID."""
    session = Session()
    try:
        return session.query(Email).filter(Email.id == email_id).first()
    finally:
        session.close()

def get_emails_by_thread(thread_id: str) -> List[Email]:
    """Retrieve all emails in a thread."""
    session = Session()
    try:
        return session.query(Email).filter(Email.thread_id == thread_id).order_by(Email.timestamp).all()
    finally:
        session.close()

def save_email(email_data: Dict[str, Any]) -> Email:
    """Save an email to the database."""
    session = Session()
    try:
        email = Email(
            id=email_data["id"],
            sender=email_data["sender"],
            recipient=email_data["recipient"],
            subject=email_data["subject"],
            body=email_data["body"],
            timestamp=email_data.get("timestamp", datetime.now()),
            thread_id=email_data["thread_id"],
            has_attachment=email_data.get("has_attachment", False)
        )
        session.add(email)
        session.commit()
        return email
    finally:
        session.close()

def save_attachment(attachment_data: Dict[str, Any]) -> Attachment:
    """Save an attachment to the database."""
    session = Session()
    try:
        attachment = Attachment(
            id=attachment_data["id"],
            email_id=attachment_data["email_id"],
            filename=attachment_data["filename"],
            content_type=attachment_data["content_type"],
            size=attachment_data["size"],
            data=attachment_data["data"]
        )
        session.add(attachment)
        session.commit()
        return attachment
    finally:
        session.close()

def save_response(response_data: Dict[str, Any]) -> Response:
    """Save a response to the database."""
    session = Session()
    try:
        response = Response(
            id=response_data["id"],
            email_id=response_data["email_id"],
            content=response_data["content"],
            timestamp=response_data.get("timestamp", datetime.now()),
            sent=response_data.get("sent", False)
        )
        session.add(response)
        session.commit()
        return response
    finally:
        session.close()

def get_all_emails(limit: int = 100) -> List[Email]:
    """Get all emails with a limit."""
    session = Session()
    try:
        return session.query(Email).order_by(Email.timestamp.desc()).limit(limit).all()
    finally:
        session.close()

# Initialize database when module is imported
init_db()
