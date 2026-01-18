from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()
from app.routers import core, admin
from app.database import engine, Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Create tables if not exist (redundant with init_db but safe)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Treehouse Library")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(core.router)
app.include_router(admin.router)

@app.on_event("startup")
def on_startup():
    """
    Startup event handler.
    Initializes the background scheduler for overdue checks and newsletters.
    """
    from app import monitor
    logger.info("Starting up Treehouse Library application...")
    monitor.start_scheduler()
