# Treehouse Library

A simple library management system for the Treehouse community, built with FastAPI. This application allows for scanning books to add, check out, or return them, managing patrons, and viewing admin insights.

## Features

- **Smart Scan Handling**: Scanned ISBNs are automatically routed to the appropriate action:
    - **Add Book**: If the book is not in the system.
    - **Checkout**: If the book is available.
    - **Return**: If the book is currently checked out.
- **Patron Management**: Automatically creates patron records during checkout if they don't exist.
- **Book Ratings & Reviews**: Users can rate and review books upon return.
- **Admin Dashboard**: View all active checkouts and force-return books if necessary.
- **Background Tasks**: Includes a scheduler for background monitoring services.

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite (via SQLAlchemy)
- **Templating**: Jinja2
- **Server**: Uvicorn

## Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd TreehouseLibrary
    ```

2.  **Create a virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To start the server, use `uvicorn`. The application entry point is `app.main:app`.

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### Application Structure

- `app/main.py`: Application entry point and startup logic.
- `app/models.py`: Database models (Book, Patron, Checkout, Rating).
- `app/routers/`: Request handlers.
    - `core.py`: Main library flows (Scan, Add, Checkout, Return).
    - `admin.py`: Admin dashboard.
- `app/templates/`: HTML templates.
- `app/static/`: CSS and JavaScript files.
- `app/monitor.py`: Scheduled background tasks.
