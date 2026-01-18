from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timedelta
from typing import List, Optional

def get_book(db: Session, isbn: str) -> Optional[models.Book]:
    """Retrieves a book by its ISBN."""
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def create_book(db: Session, isbn: str, title: str, author: str, our_review: str = None, our_rating: int = None) -> models.Book:
    """Creates a new book."""
    db_book = models.Book(isbn=isbn, title=title, author=author, our_review=our_review, our_rating=our_rating)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_patron_by_name(db: Session, name: str) -> Optional[models.Patron]:
    """Retrieves a patron by their name."""
    return db.query(models.Patron).filter(models.Patron.name == name).first()

def create_patron(db: Session, name: str, email: str) -> models.Patron:
    """Creates a new patron."""
    db_patron = models.Patron(name=name, email=email)
    db.add(db_patron)
    db.commit()
    db.refresh(db_patron)
    return db_patron

def create_checkout(db: Session, book_isbn: str, patron_id: int) -> models.Checkout:
    """Creates a new checkout record for a book."""
    db_checkout = models.Checkout(book_isbn=book_isbn, patron_id=patron_id)
    db.add(db_checkout)
    db.commit()
    db.refresh(db_checkout)
    return db_checkout

def return_checkout(db: Session, checkout_id: int) -> Optional[models.Checkout]:
    """Marks a checkout as returned."""
    db_checkout = db.query(models.Checkout).filter(models.Checkout.id == checkout_id).first()
    if db_checkout:
        db_checkout.returned_at = datetime.now()
        db.commit()
        db.refresh(db_checkout)
    return db_checkout

def get_active_checkout_by_book(db: Session, isbn: str) -> Optional[models.Checkout]:
    """gets the active (not returned) checkout for a specific book."""
    return db.query(models.Checkout).filter(
        models.Checkout.book_isbn == isbn,
        models.Checkout.returned_at == None
    ).first()

def create_rating(db: Session, book_isbn: str, patron_name: str, star_rating: int, review_content: str = None, patron_id: int = None) -> models.Rating:
    """Creates a new rating/review for a book."""
    db_rating = models.Rating(
        book_isbn=book_isbn, 
        patron_name=patron_name, 
        star_rating=star_rating, 
        review_content=review_content,
        patron_id=patron_id
    )
    db.add(db_rating)
    db.commit()
    return db_rating

def get_all_active_checkouts(db: Session) -> List[models.Checkout]:
    """Retrieves all currently active checkouts."""
    return db.query(models.Checkout).filter(models.Checkout.returned_at == None).all()

def get_overdue_checkouts(db: Session, days: int = 21) -> List[models.Checkout]:
    """Retrieves checkouts that are overdue (older than 'days' and not returned)."""
    cutoff = datetime.now() - timedelta(days=days)
    return db.query(models.Checkout).filter(
        models.Checkout.returned_at == None,
        models.Checkout.checked_out_at < cutoff
    ).all()

def create_reminder_log(db: Session, checkout_id: int, status: str) -> models.ReminderLog:
    """Logs a reminder attempt."""
    db_reminder = models.ReminderLog(checkout_id=checkout_id, status=status)
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminder_logs(db: Session, limit: int = 50) -> List[models.ReminderLog]:
    """Retrieves the most recent reminder logs."""
    return db.query(models.ReminderLog).order_by(models.ReminderLog.sent_at.desc()).limit(limit).all()

def get_books_added_since(db: Session, date: datetime) -> List[models.Book]:
    """Retrieves books added on or after a specific date."""
    return db.query(models.Book).filter(models.Book.created_at >= date).all()

def get_all_patrons(db: Session) -> List[models.Patron]:
    """Retrieves all patrons."""
    return db.query(models.Patron).all()

def get_all_books(db: Session) -> List[models.Book]:
    """Retrieves all books ordered by title."""
    return db.query(models.Book).order_by(models.Book.title).all()

def update_book(db: Session, isbn: str, title: str, author: str, our_review: str = None, our_rating: int = None) -> Optional[models.Book]:
    """Updates an existing book's details."""
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        db_book.title = title
        db_book.author = author
        db_book.our_review = our_review
        db_book.our_rating = our_rating
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, isbn: str) -> bool:
    """Deletes a book from the database."""
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        return True
    return False

def get_checkout_history(db: Session, limit: int = 100) -> List[models.Checkout]:
    """Retrieves the checkout history ordered by checkout date."""
    return db.query(models.Checkout).order_by(models.Checkout.checked_out_at.desc()).limit(limit).all()
