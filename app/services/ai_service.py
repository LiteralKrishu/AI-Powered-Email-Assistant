from openai import OpenAI
from typing import List, Dict, Any
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_response(email_subject: str, email_body: str, sentiment: str, 
                     extracted_info: Dict[str, Any], knowledge_context: List[str] = None) -> str:
    """
    Generate AI response for an email
    """
    if not settings.OPENAI_API_KEY or not client:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    try:
        # Prepare context from knowledge base
        context = ""
        if knowledge_context:
            context = "Relevant information:\n" + "\n".join([f"- {item}" for item in knowledge_context])
        
        prompt = f"""
        You are a customer support agent. Draft a professional and empathetic response to the following email.
        Consider the customer's sentiment: {sentiment}
        
        {context}
        
        Email Subject: {email_subject}
        Email Body: {email_body}
        
        Extracted information that might be relevant:
        {extracted_info}
        
        Please draft a response that addresses the customer's concerns. Be helpful, professional, and empathetic.
        If you need more information from the customer, politely ask for it.
        Keep the response concise but thorough.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful customer support agent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return f"Error generating response: {str(e)}"

def search_knowledge_base(query: str, knowledge_items: List[Any]) -> List[str]:
    """
    Simple search through knowledge base items
    """
    if not knowledge_items:
        return []
    
    # Simple keyword matching for now
    # In a production system, you'd use embeddings and vector search
    query_lower = query.lower()
    relevant_items = []
    
    for item in knowledge_items:
        content = f"{item.title} {item.content}".lower()
        if any(keyword in content for keyword in query_lower.split()):
            relevant_items.append(f"{item.title}: {item.content[:200]}...")
    
    return relevant_items[:3]  # Return top 3 most relevant items
