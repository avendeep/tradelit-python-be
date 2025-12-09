
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service to send emails using SMTP.
    """
    
    @staticmethod
    async def send_email(subject: str, body: str):
        """
        Send an email asynchronously (wrapped).
        
        Args:
            subject: Email subject
            body: Email body (HTML supported)
        """
        # In a real async app, we might want to run this blocking call in a separate thread
        # if the SMTP server is slow. For now, we'll keep it simple or wrap in run_in_executor if needed,
        # but since this is designed to run in BackgroundTasks, standard blocking calls are acceptable 
        # as FastAPI handles them well in thread pools.
        
        try:
            sender_email = settings.EMAIL_FROM
            receiver_email = settings.EMAIL_TO
            password = settings.SMTP_PASSWORD
            smtp_server = settings.SMTP_SERVER
            smtp_port = settings.SMTP_PORT

            if not all([sender_email, receiver_email, password, smtp_server, smtp_port]):
                logger.warning("⚠️ Email configuration missing. Skipping email send.")
                return

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            # Handle multiple recipients if comma separated
            if "," in receiver_email:
                message["To"] = receiver_email
                recipients = [r.strip() for r in receiver_email.split(",")]
            else:
                message["To"] = receiver_email
                recipients = [receiver_email]

            # Turn these into plain/html MIMEText objects
            # For simplicity, we assume the body passed is HTML formatted or plain text that looks okay
            part = MIMEText(body, "html")
            message.attach(part)


            # Create secure connection with server and send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, recipients, message.as_string())
            
            logger.info(f"📧 Email sent successfully: {subject}")

        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")

email_service = EmailService()
