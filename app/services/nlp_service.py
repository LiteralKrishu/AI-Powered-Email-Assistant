from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import re
from typing import Dict, Any
import logging
from ..config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentiment analysis model
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except:
    logger.warning("Could not load sentiment analysis model, using fallback")
    sentiment_analyzer = None

def analyze_sentiment(text: str) -> tuple:
    """
    Analyze sentiment of email text
    """
    if not text.strip():
        return "neutral", 0.0
    
    try:
        if sentiment_analyzer:
            # Limit text length for the model
            if len(text) > 512:
                text = text[:512]
            
            result = sentiment_analyzer(text)[0]
            return result['label'].lower(), result['score']
        else:
            # Fallback simple sentiment analysis
            positive_words = ["good", "great", "excellent", "awesome", "fantastic", "thanks", "thank you", "helpful", "appreciate"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointed", "frustrated", "angry", "upset", "problem", "issue"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return "positive", 0.7
            elif negative_count > positive_count:
                return "negative", 0.7
            else:
                return "neutral", 0.5
                
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return "neutral", 0.5

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract entities from email text using regex patterns
    """
    entities = {
        "phone_numbers": extract_phone_numbers(text),
        "email_addresses": extract_email_addresses(text),
        "urls": extract_urls(text),
        "important_keywords": extract_important_keywords(text)
    }
    return entities

def extract_phone_numbers(text: str):
    phone_regex = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    return re.findall(phone_regex, text)

def extract_email_addresses(text: str):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_regex, text)

def extract_urls(text: str):
    url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    return re.findall(url_regex, text)

def extract_important_keywords(text: str):
    important_keywords = [
        "urgent", "asap", "immediately", "emergency", "important",
        "critical", "broken", "not working", "error", "bug",
        "payment", "invoice", "refund", "account", "login"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    for keyword in important_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def detect_urgency(text: str) -> int:
    """
    Detect urgency level based on keywords (scale 1-5)
    """
    urgency_keywords = {
        "urgent": 5, "asap": 5, "immediately": 5, "emergency": 5, "right away": 5,
        "important": 4, "critical": 4, "soon": 3, "quickly": 3,
        "when you can": 2, "no rush": 1, "whenever": 1, "at your convenience": 1
    }
    
    text_lower = text.lower()
    max_urgency = 1
    
    for keyword, level in urgency_keywords.items():
        if keyword in text_lower and level > max_urgency:
            max_urgency = level
    
    return max_urgency
