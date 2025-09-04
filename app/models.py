from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    sender = Column(String, index=True)
    recipient = Column(String)
    subject = Column(String)
    body = Column(Text)
    date = Column(DateTime)
    sentiment = Column(String)  # positive, neutral, negative
    sentiment_score = Column(Float)  # Confidence score
    urgency = Column(Integer)  # 1-5 scale
    category = Column(String)  # Support, Billing, Technical, etc.
    extracted_info = Column(JSON)  # JSON with extracted entities
    is_processed = Column(Boolean, default=False)
    ai_response = Column(Text)
    is_response_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    category = Column(String)
    tags = Column(JSON)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
