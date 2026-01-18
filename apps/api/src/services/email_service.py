from flask_mail import Message
from utils.mail import mail
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def send_email(self, recipient: str, subject: str, body: str, html: str = None):
        """Send an email to a single recipient."""
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body,
                html=html,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            # In development, we don't want to fail the whole process if email fails
            if current_app.config.get('DEBUG'):
                print(f"DEBUG EMAIL ERROR: {str(e)}")
            return False

    def notify_user(self, user, subject: str, message: str):
        """Helper to send email if user has email address."""
        if hasattr(user, 'email') and user.email:
            return self.send_email(user.email, subject, message)
        return False
