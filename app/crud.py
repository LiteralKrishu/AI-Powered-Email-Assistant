from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import models, schemas
from datetime import datetime, timedelta

def get_email(db: Session, email_id: int):
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def get_email_by_message_id(db: Session, message_id: str):
    return db.query(models.Email).filter(models.Email.message_id == message_id).first()

def get_emails(db: Session, skip: int = 0, limit: int = 100, 
               urgency: int = None, sentiment: str = None, 
               category: str = None, processed: bool = None):
    query = db.query(models.Email)
    
    if urgency is not None:
        query = query.filter(models.Email.urgency == urgency)
    if sentiment is not None:
        query = query.filter(models.Email.sentiment == sentiment)
    if category is not None:
        query = query.filter(models.Email.category == category)
    if processed is not None:
        query = query.filter(models.Email.is_processed == processed)
    
    return query.order_by(desc(models.Email.date)).offset(skip).limit(limit).all()

def create_email(db: Session, email: schemas.EmailCreate):
    db_email = models.Email(
        message_id=email.message_id,
        sender=email.sender,
        recipient=email.recipient,
        subject=email.subject,
        body=email.body,
        date=email.date,
        sentiment=email.sentiment,
        sentiment_score=email.sentiment_score,
        urgency=email.urgency,
        category=email.category,
        extracted_info=email.extracted_info
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def update_email(db: Session, email_id: int, email_update: schemas.EmailUpdate):
    db_email = db.query(models.Email).filter(models.Email.id == email_id).first()
    if db_email:
        for key, value in email_update.dict(exclude_unset=True).items():
            setattr(db_email, key, value)
        db.commit()
        db.refresh(db_email)
    return db_email

def get_analytics(db: Session):
    # Total emails
    total_emails = db.query(models.Email).count()
    
    # Processed emails
    processed_emails = db.query(models.Email).filter(models.Email.is_processed == True).count()
    
    # Pending emails
    pending_emails = total_emails - processed_emails
    
    # Sentiment distribution
    sentiment_distribution = db.query(
        models.Email.sentiment, 
        func.count(models.Email.sentiment)
    ).group_by(models.Email.sentiment).all()
    sentiment_distribution = {s: c for s, c in sentiment_distribution if s}
    
    # Urgency distribution
    urgency_distribution = db.query(
        models.Email.urgency, 
        func.count(models.Email.urgency)
    ).group_by(models.Email.urgency).all()
    urgency_distribution = {f"Level {u}": c for u, c in urgency_distribution if u}
    
    # Category distribution
    category_distribution = db.query(
        models.Email.category, 
        func.count(models.Email.category)
    ).group_by(models.Email.category).all()
    category_distribution = {c: count for c, count in category_distribution if c}
    
    # Emails in last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    emails_last_24h = db.query(models.Email).filter(models.Email.created_at >= last_24h).count()
    
    return {
        "total_emails": total_emails,
        "processed_emails": processed_emails,
        "pending_emails": pending_emails,
        "sentiment_distribution": sentiment_distribution,
        "urgency_distribution": urgency_distribution,
        "category_distribution": category_distribution,
        "emails_last_24h": emails_last_24h
    }

def create_knowledge_base_item(db: Session, kb_item: schemas.KnowledgeBaseCreate):
    db_kb = models.KnowledgeBase(
        title=kb_item.title,
        content=kb_item.content,
        category=kb_item.category,
        tags=kb_item.tags
    )
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)
    return db_kb

def get_knowledge_base_items(db: Session, skip: int = 0, limit: int = 100, category: str = None):
    query = db.query(models.KnowledgeBase)
    if category:
        query = query.filter(models.KnowledgeBase.category == category)
    return query.order_by(desc(models.KnowledgeBase.updated_at)).offset(skip).limit(limit).all()
