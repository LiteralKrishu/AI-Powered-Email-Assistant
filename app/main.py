from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app import models, schemas, crud
from app.database import get_db, engine
from app.services.email_service import fetch_emails, categorize_email
from app.services.nlp_service import analyze_sentiment, extract_entities, detect_urgency
from app.services.ai_service import generate_response, search_knowledge_base
from app.services.response_service import send_email_response
from app.config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Email Support Automation System"}

@app.post("/fetch-emails/", response_model=schemas.StatusResponse)
def fetch_and_process_emails(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        # Fetch emails from email server
        raw_emails = fetch_emails()
        
        processed_count = 0
        for email_data in raw_emails:
            # Check if email already exists
            existing_email = crud.get_email_by_message_id(db, email_data["message_id"])
            if existing_email:
                continue
                
            # Process email with NLP
            sentiment, sentiment_score = analyze_sentiment(email_data["body"])
            entities = extract_entities(email_data["body"])
            urgency = detect_urgency(email_data["body"])
            category = categorize_email(email_data["subject"], email_data["body"])
            
            # Create email in database
            db_email = schemas.EmailCreate(
                message_id=email_data["message_id"],
                sender=email_data["sender"],
                recipient=email_data["recipient"],
                subject=email_data["subject"],
                body=email_data["body"],
                date=email_data["date"],
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                urgency=urgency,
                category=category,
                extracted_info=entities
            )
            
            crud.create_email(db, db_email)
            processed_count += 1
            
            # Add background task to generate AI response
            background_tasks.add_task(generate_ai_response_for_email, db, email_data["message_id"])
            
        return {"status": "success", "message": f"Processed {processed_count} new emails", "count": processed_count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_ai_response_for_email(db: Session, message_id: str):
    """
    Background task to generate AI response for an email
    """
    email = crud.get_email_by_message_id(db, message_id)
    if not email:
        return
    
    # Get knowledge base items for context
    knowledge_items = crud.get_knowledge_base_items(db, category=email.category)
    
    # Search for relevant knowledge
    query = f"{email.subject} {email.body[:100]}"
    knowledge_context = search_knowledge_base(query, knowledge_items)
    
    # Generate AI response
    ai_response = generate_response(
        email.subject, 
        email.body, 
        email.sentiment, 
        email.extracted_info,
        knowledge_context
    )
    
    # Update email with AI response
    crud.update_email(db, email.id, schemas.EmailUpdate(ai_response=ai_response, is_processed=True))

@app.get("/emails/", response_model=List[schemas.Email])
def read_emails(skip: int = 0, limit: int = 100, 
                urgency: int = None, sentiment: str = None, 
                category: str = None, processed: bool = None,
                db: Session = Depends(get_db)):
    emails = crud.get_emails(db, skip=skip, limit=limit, 
                            urgency=urgency, sentiment=sentiment, 
                            category=category, processed=processed)
    return emails

@app.get("/emails/{email_id}", response_model=schemas.Email)
def read_email(email_id: int, db: Session = Depends(get_db)):
    db_email = crud.get_email(db, email_id=email_id)
    if db_email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_email

@app.put("/emails/{email_id}", response_model=schemas.Email)
def update_email(email_id: int, email_update: schemas.EmailUpdate, db: Session = Depends(get_db)):
    db_email = crud.update_email(db, email_id, email_update)
    if db_email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_email

@app.post("/emails/{email_id}/send-response")
def send_response(email_id: int, db: Session = Depends(get_db)):
    email = crud.get_email(db, email_id=email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    if not email.ai_response:
        raise HTTPException(status_code=400, detail="No AI response generated for this email")
    
    # Send email response
    success = send_email_response(email.sender, email.subject, email.ai_response)
    
    if success:
        # Update email as response sent
        crud.update_email(db, email_id, schemas.EmailUpdate(is_response_sent=True))
        return {"status": "success", "message": "Response sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send response")

@app.get("/analytics/", response_model=schemas.AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    analytics = crud.get_analytics(db)
    return analytics

@app.post("/knowledge-base/", response_model=schemas.KnowledgeBase)
def create_knowledge_item(kb_item: schemas.KnowledgeBaseCreate, db: Session = Depends(get_db)):
    return crud.create_knowledge_base_item(db, kb_item)

@app.get("/knowledge-base/", response_model=List[schemas.KnowledgeBase])
def read_knowledge_items(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    return crud.get_knowledge_base_items(db, skip=skip, limit=limit, category=category)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
