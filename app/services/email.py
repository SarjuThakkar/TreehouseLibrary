import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
import logging
from typing import List

# Configure logging
logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email using Gmail SMTP.
    Requires GMAIL_USER and GMAIL_PASSWORD environment variables to be set.
    """
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')

    if not all([gmail_user, gmail_password]):
        logger.warning("Gmail credentials not set. Skipping email.")
        return False

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_bulk_emails(recipients: List[str], subject: str, body: str, delay_seconds: float = 1.0) -> int:
    """
    Sends emails to a list of recipients with a delay between each to avoid rate limits.
    Returns the count of successfully sent emails.
    """
    count = 0
    for email in recipients:
        if send_email(email, subject, body):
            count += 1
        time.sleep(delay_seconds)
    return count

def send_overdue_notice(email: str, book_title: str) -> bool:
    """
    Convenience function to send an overdue book notice.
    """
    subject = "Reminder from the Treehouse Library"
    body = f"Hello! This is an automated reminder that '{book_title}' has been checked out for a while! If you are done with it, come back and exchange it for another book!"
    return send_email(email, subject, body)
