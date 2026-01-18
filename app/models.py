from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Book(Base):
    """
    Represents a book in the library.
    """
    __tablename__ = "books"

    isbn = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    our_review = Column(Text, nullable=True)
    our_rating = Column(Integer, nullable=True) # 1-5
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    checkouts = relationship("Checkout", back_populates="book")
    ratings = relationship("Rating", back_populates="book")

    @property
    def is_checked_out(self):
        """
        Returns True if the book is currently checked out, False otherwise.
        """
        # This is a bit complex in pure SQLA models without a query, 
        # but we can check if there is an active checkout.
        # For simplicity in templates, we might resolve this in the crud/route layer or use a helper method.
        # But let's look at the active checkouts relationship
        for checkout in self.checkouts:
            if checkout.returned_at is None:
                return True
        return False

class Patron(Base):
    """
    Represents a library patron.
    """
    __tablename__ = "patrons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)

    checkouts = relationship("Checkout", back_populates="patron")

class Checkout(Base):
    """
    Represents a record of a book being checked out by a patron.
    """
    __tablename__ = "checkouts"

    id = Column(Integer, primary_key=True, index=True)
    book_isbn = Column(String, ForeignKey("books.isbn"))
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    checked_out_at = Column(DateTime, default=datetime.now)
    returned_at = Column(DateTime, nullable=True)
    last_reminder_sent_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="checkouts")
    patron = relationship("Patron", back_populates="checkouts")

class Rating(Base):
    """
    Represents a rating and/or review given by a patron for a book.
    """
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    book_isbn = Column(String, ForeignKey("books.isbn"))
    patron_name = Column(String) # For "Patron name (free text)" requirement
    patron_id = Column(Integer, ForeignKey("patrons.id"), nullable=True) # Optional link
    star_rating = Column(Integer)
    review_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    book = relationship("Book", back_populates="ratings")

class ReminderLog(Base):
    """
    Logs history of reminder emails sent for checkouts.
    """
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    checkout_id = Column(Integer, ForeignKey("checkouts.id"))
    sent_at = Column(DateTime, default=datetime.now)
    status = Column(String) # "sent", "failed"

    checkout = relationship("Checkout", back_populates="reminders")

# Update Checkout to include back_populates
Checkout.reminders = relationship("ReminderLog", back_populates="checkout")
