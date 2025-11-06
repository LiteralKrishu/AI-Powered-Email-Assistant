import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_emails() -> List[Dict]:
    """
    Fetch unread emails from IMAP server
    """
    emails = []
    
    try:
        # Connect to IMAP server
        logger.info(f"Connecting to {settings.EMAIL_SERVER}:{settings.EMAIL_PORT}")
        mail = imaplib.IMAP4_SSL(settings.EMAIL_SERVER, settings.EMAIL_PORT)
        
        # Login
        logger.info(f"Logging in as {settings.EMAIL_USER}")
        mail.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        
        # Select inbox
        mail.select("inbox")
        
        # Search for unread emails from last 24 hours
        date_since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE {date_since})')
        
        if status == "OK":
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")
            
            for num in email_ids:
                status, data = mail.fetch(num, '(RFC822)')
                
                if status == "OK":
                    msg = email.message_from_bytes(data[0][1])
                    
                    # Decode subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Decode sender
                    sender, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode(encoding if encoding else "utf-8")
                    
                    # Extract email address from sender
                    email_match = re.search(r'<(.+?)>', sender)
                    if email_match:
                        sender_email = email_match.group(1)
                    else:
                        sender_email = sender
                    
                    # Get email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    body = part.get_payload(decode=True).decode('latin-1')
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            body = msg.get_payload(decode=True).decode('latin-1')
                    
                    # Parse date
                    date_str = msg["Date"]
                    try:
                        date_tuple = email.utils.parsedate_tz(date_str)
                        if date_tuple:
                            date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        else:
                            date = datetime.now()
                    except:
                        date = datetime.now()
                    
                    email_data = {
                        "message_id": msg["Message-ID"] or f"{datetime.now().timestamp()}-{sender_email}",
                        "sender": sender_email,
                        "recipient": msg["To"],
                        "subject": subject or "No Subject",
                        "body": body or "",
                        "date": date
                    }
                    
                    # Filter for support-related emails
                    if is_support_email(subject, body):
                        emails.append(email_data)
                    else:
                        logger.info(f"Skipping non-support email: {subject}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
    
    return emails

def is_support_email(subject: str, body: str) -> bool:
    """
    Check if email is support-related based on keywords
    """
    support_keywords = [
        "support", "help", "question", "issue", "problem",
        "assistance", "trouble", "error", "bug", "fix",
        "not working", "how to", "why", "what", "when",
        "where", "can't", "cannot", "broken", "complaint"
    ]
    
    content = (subject + " " + body).lower()
    return any(keyword in content for keyword in support_keywords)

def categorize_email(subject: str, body: str) -> str:
    """
    Categorize email based on content
    """
    content = (subject + " " + body).lower()
    
    categories = {
        "billing": ["payment", "invoice", "bill", "charge", "price", "cost", "refund"],
        "technical": ["error", "bug", "crash", "not working", "broken", "technical", "server"],
        "account": ["login", "password", "account", "sign up", "register", "profile"],
        "feature": ["feature", "request", "suggestion", "idea", "improvement"],
        "general": ["question", "help", "information", "how to", "what is"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return "general"
