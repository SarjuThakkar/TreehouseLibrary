from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app import crud, database, models
from app import monitor
import time

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(database.get_db)):
    """
    Renders the admin dashboard.
    Shows active checkouts, reminder logs, book inventory, and recent history.
    """
    checkouts = crud.get_all_active_checkouts(db)
    logs = crud.get_reminder_logs(db)
    books = crud.get_all_books(db)
    history = crud.get_checkout_history(db)
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "checkouts": checkouts,
        "logs": logs,
        "books": books,
        "history": history,
        "now": datetime.now()
    })

@router.post("/return/{checkout_id}")
def admin_force_return(checkout_id: int, db: Session = Depends(database.get_db)):
    """
    Allows an admin to force return a book (e.g. if the physical book was returned without scanning).
    """
    crud.return_checkout(db, checkout_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/book/{isbn}/edit", response_class=HTMLResponse)
def admin_edit_book_form(request: Request, isbn: str, db: Session = Depends(database.get_db)):
    """
    Renders the edit book form.
    """
    book = crud.get_book(db, isbn)
    if not book:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("book_edit.html", {"request": request, "book": book})

@router.post("/book/{isbn}/edit")
def admin_edit_book(
    request: Request,
    isbn: str,
    title: str = Form(...),
    author: str = Form(...),
    our_review: str = Form(None),
    our_rating: int = Form(None),
    db: Session = Depends(database.get_db)
):
    """
    Handles the edit book form submission.
    Updates book details.
    """
    crud.update_book(db, isbn=isbn, title=title, author=author, our_review=our_review, our_rating=our_rating)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/book/{isbn}/delete")
def admin_delete_book(isbn: str, db: Session = Depends(database.get_db)):
    """
    Deletes a book from the library.
    """
    crud.delete_book(db, isbn)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/blast")
def admin_email_blast(request: Request, subject: str = Form(...), message: str = Form(...), db: Session = Depends(database.get_db)):
    """
    Sends an email blast to all patrons.
    """
    # 1. Get all patrons
    patrons = crud.get_all_patrons(db)
    from app.services import email
    
    count = 0
    for patron in patrons:
        if patron.email:
            # We must use send_email from services
            if email.send_email(patron.email, subject, message):
                count += 1
            time.sleep(1) # Rate limiting
                
    # We could flash a message here if we had flash messaging, 
    # but for now just redirect back.
    # Ideally, pass a query param or something?
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/trigger-overdue-check")
def admin_trigger_overdue_check(db: Session = Depends(database.get_db)):
    """
    Manually triggers the overdue book check.
    """
    monitor.check_overdue_books()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/trigger-newsletter")
def admin_trigger_newsletter(db: Session = Depends(database.get_db)):
    """
    Manually triggers the monthly newsletter.
    """
    monitor.send_monthly_newsletter()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

