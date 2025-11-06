import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_response(recipient: str, subject: str, body: str, reply_to: str = None) -> bool:
    """
    Send an email response
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_USER
        msg['To'] = recipient
        msg['Subject'] = f"Re: {subject}"
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP_SSL(settings.EMAIL_SERVER, 465)
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.EMAIL_USER, recipient, text)
        server.quit()
        
        logger.info(f"Email sent to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False
