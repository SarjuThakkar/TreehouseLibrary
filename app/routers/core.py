from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import crud, models, database

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Renders the home page with the scanner interface.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/scan")
def scan_isbn(request: Request, isbn: str = Form(...), db: Session = Depends(database.get_db)):
    """
    Processes a scanned ISBN.
    Redirects to:
    - Add Book form if the book doesn't exist.
    - Return Book form if the book is currently checked out.
    - Checkout Book form if the book is available.
    """
    # Clean ISBN? Requirement says scanner sends Enter.
    isbn = isbn.strip()
    book = crud.get_book(db, isbn)
    
    if not book:
        # Case A: Book NOT in database
        return RedirectResponse(url=f"/book/{isbn}/add", status_code=status.HTTP_303_SEE_OTHER)
    
    if book.is_checked_out:
        # Case B: Book IS in database AND checked out
        return RedirectResponse(url=f"/book/{isbn}/return", status_code=status.HTTP_303_SEE_OTHER)
    
    # Case C: Book IS in database AND available
    return RedirectResponse(url=f"/book/{isbn}/checkout", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/book/{isbn}/add", response_class=HTMLResponse)
def add_book_form(request: Request, isbn: str):
    """
    Renders the form to add a new book.
    """
    return templates.TemplateResponse("book_add.html", {"request": request, "isbn": isbn})

@router.post("/book/{isbn}/add")
def add_book(
    request: Request, 
    isbn: str, 
    title: str = Form(...), 
    author: str = Form(...), 
    our_review: str = Form(None), 
    our_rating: int = Form(None),
    db: Session = Depends(database.get_db)
):
    """
    Handles the submission of the add book form.
    Creates a new book record.
    """
    crud.create_book(db, isbn=isbn, title=title, author=author, our_review=our_review, our_rating=our_rating)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/book/{isbn}/checkout", response_class=HTMLResponse)
def checkout_book_form(request: Request, isbn: str, db: Session = Depends(database.get_db)):
    """
    Renders the checkout form for a specific book.
    """
    book = crud.get_book(db, isbn)
    if not book:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse("book_details.html", {"request": request, "book": book})

@router.post("/book/{isbn}/checkout")
def checkout_book(
    request: Request, 
    isbn: str, 
    patron_name: str = Form(...), 
    email: str = Form(...), 
    db: Session = Depends(database.get_db)
):
    """
    Handles the checkout process.
    Creates or retrieves the patron, then creates a checkout record.
    """
    # Check if patron exists, else create
    patron = crud.get_patron_by_name(db, patron_name)
    if not patron:
        patron = crud.create_patron(db, name=patron_name, email=email)
    
    crud.create_checkout(db, book_isbn=isbn, patron_id=patron.id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/book/{isbn}/return", response_class=HTMLResponse)
def return_book_form(request: Request, isbn: str, db: Session = Depends(database.get_db)):
    """
    Renders the return book form.
    Includes patron info if available.
    """
    book = crud.get_book(db, isbn)
    if not book:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Fetch active checkout to get the patron's name
    active_checkout = crud.get_active_checkout_by_book(db, isbn)
    patron_name = active_checkout.patron.name if active_checkout and active_checkout.patron else None
    
    return templates.TemplateResponse("book_return.html", {"request": request, "book": book, "patron_name": patron_name})

@router.post("/book/{isbn}/return")
def return_book(
    request: Request, 
    isbn: str, 
    star_rating: int = Form(None),
    review_content: str = Form(None),
    db: Session = Depends(database.get_db)
):
    """
    Handles the return book process.
    Marks the checkout as returned and optionally saves a rating/review.
    """
    # 1. Get active checkout to identify patron
    active_checkout = crud.get_active_checkout_by_book(db, isbn)
    
    patron_id = None
    patron_name = "Anonymous"
    
    if active_checkout:
        patron_id = active_checkout.patron_id
        if active_checkout.patron:
            patron_name = active_checkout.patron.name
        
        # Mark returned
        crud.return_checkout(db, active_checkout.id)
    
    # 2. Save rating ONLY if star_rating is provided AND > 0
    if star_rating is not None and star_rating > 0:
        crud.create_rating(
            db, 
            book_isbn=isbn, 
            patron_name=patron_name, 
            star_rating=star_rating, 
            review_content=review_content,
            patron_id=patron_id
        )
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/api/patrons")
def search_patrons(q: str = "", db: Session = Depends(database.get_db)):
    """
    API endpoint for searching patrons by name.
    Used for autocomplete in the frontend.
    """
    if not q:
        return []
    patrons = db.query(models.Patron).filter(models.Patron.name.ilike(f"%{q}%")).limit(10).all()
    return [{"name": p.name, "email": p.email} for p in patrons]
