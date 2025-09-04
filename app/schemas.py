from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List

class EmailBase(BaseModel):
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    date: datetime

class EmailCreate(EmailBase):
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    urgency: Optional[int] = None
    category: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None

class Email(EmailBase):
    id: int
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    urgency: Optional[int]
    category: Optional[str]
    extracted_info: Optional[Dict[str, Any]]
    is_processed: bool
    ai_response: Optional[str]
    is_response_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmailUpdate(BaseModel):
    ai_response: Optional[str]
    is_response_sent: Optional[bool]

class StatusResponse(BaseModel):
    status: str
    message: str
    count: Optional[int] = 0

class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[List[str]] = []

class KnowledgeBase(KnowledgeBaseCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    total_emails: int
    processed_emails: int
    pending_emails: int
    sentiment_distribution: Dict[str, int]
    urgency_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    emails_last_24h: int
