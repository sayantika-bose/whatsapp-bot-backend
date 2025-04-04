import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.database import init_db
from routers import auth, questions, users, webhook

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"))  # Logs to file
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(redirect_slashes=False)

origins = [
    "https://admin.myadvisor.sg",
    "http://localhost:3000",  # If testing locally
]

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(users.router)
app.include_router(webhook.router)

# Initialize database
logger.info("Initializing database...")
init_db()
logger.info("Database initialized successfully.")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application with uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8000)