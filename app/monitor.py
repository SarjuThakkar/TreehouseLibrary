from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from app import crud, database, models
from app.services import email
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

def check_overdue_books():
    """
    Scheduled job to check for overdue books and send email notifications.
    Runs daily at 10:00 AM.
    """
    logger.info("Running overdue book check...")
    db = database.SessionLocal()
    try:
        overdue = crud.get_overdue_checkouts(db)
        count = 0
        for checkout in overdue:
            # Simple check: if we haven't sent a reminder today?
            # or if we ever sent one? 
            # Requirement logic wasn't fully specified, but let's assume we send if no reminder sent yet 
            # OR if it's been > 7 days since last reminder.
            should_send = False
            if not checkout.last_reminder_sent_at:
                should_send = True
            else:
                days_since_last = (datetime.now() - checkout.last_reminder_sent_at).days
                if days_since_last >= 7:
                    should_send = True
            
            if should_send:
                # Get patron email from relationship
                patron_email = checkout.patron.email if checkout.patron else None
                book_title = checkout.book.title if checkout.book else "Unknown Book"
                
                if patron_email:
                    sent_successfully = email.send_overdue_notice(patron_email, book_title)
                    status = "sent" if sent_successfully else "failed"
                    
                    crud.create_reminder_log(db, checkout_id=checkout.id, status=status)
                    
                    if sent_successfully:
                        checkout.last_reminder_sent_at = datetime.now()
                        count += 1
                else:
                    logger.warning(f"Checkout {checkout.id} has no patron email associated.")
        
        if count > 0:
            db.commit()
            logger.info(f"Sent {count} reminders.")
        else:
            logger.info("No new reminders to send.")
            
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}")
    finally:
        db.close()

def send_monthly_newsletter():
    """
    Scheduled job to send a monthly newsletter with new book arrivals.
    Runs on the 1st of every month at 11:00 AM.
    """
    logger.info("Running monthly newsletter check...")
    db = database.SessionLocal()
    try:
        # 1. Get books added in the last 30 days
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=30)
        new_books = crud.get_books_added_since(db, cutoff)
        
        if not new_books:
            logger.info("No new books added this month. Skipping newsletter.")
            return

        # 2. Construct message
        titles = [b.title for b in new_books]
        # Truncate if too long? For now, list them all.
        book_list = ", ".join(titles)
        message = f"New at Treehouse Library this month: {book_list}. Come check them out!"
        
        # 3. Get all patrons
        patrons = crud.get_all_patrons(db)
        
        count = 0
        for patron in patrons:
            if patron.email:
                if email.send_email(patron.email, "New at the Treehouse Library 📚", message):
                    count += 1
                time.sleep(1) # Rate limiting
        
        logger.info(f"Sent newsletter to {count} patrons.")
        
    except Exception as e:
        logger.error(f"Error in newsletter job: {e}")
    finally:
        db.close()

def start_scheduler():
    """
    Initializes and starts the background scheduler for periodic tasks.
    """
    scheduler = BackgroundScheduler()
    
    # Existing job: Overdue checks daily at 10 AM
    scheduler.add_job(check_overdue_books, 'cron', hour=10, minute=0)
    
    # New job: Newsletter on the 1st of every month at 11 AM
    scheduler.add_job(send_monthly_newsletter, 'cron', day=1, hour=11, minute=0)
    
    scheduler.start()
    logger.info("Scheduler started.")
    logger.info("- 'check_overdue_books' scheduled for 10:00 AM daily.")
    logger.info("- 'send_monthly_newsletter' scheduled for 1st of month at 11:00 AM.")
