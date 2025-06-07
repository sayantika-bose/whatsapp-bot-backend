import logging
import os
import threading
import time
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.database import init_db
from routers import (
    auth, financial_advisors, investor_profiles, questions, quiz_answers,
    quiz_questions, user_answers, user_investor_profile, users, webhook,
    config_router, submit_form
)
from services.auth_service import decode_token

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Logging setup
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
    ]
)

logger = logging.getLogger(__name__)

# Load .env
load_dotenv()
SECRET_SALT = os.getenv("SECRET_SALT")

def validate_secret_salt(x_api_key: str = Header(...)):
    if x_api_key != SECRET_SALT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )

# Watcher Class
class DotEnvChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".env"):
            logger.info(".env file changed, reloading environment variables...")
            time.sleep(0.2)  # Wait for file write to finish
            try:
                load_dotenv(override=True)
            except PermissionError:
                logger.warning("Permission denied when reading .env, retrying...")
                time.sleep(0.5)
                try:
                    load_dotenv(override=True)
                except Exception as e:
                    logger.error(f"Failed to reload .env: {e}")

def start_env_watcher():
    event_handler = DotEnvChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    logger.info("Started .env file watcher")

    def watch():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    thread = threading.Thread(target=watch, daemon=True)
    thread.start()

# FastAPI App Setup
app = FastAPI(redirect_slashes=False)

origins = [
    "https://admin.myadvisor.sg",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(submit_form.router)

app.include_router(
    user_answers.router,
    prefix="/user-answers",
    tags=["User Answers"],
    dependencies=[Depends(validate_secret_salt)]
)

app.include_router(
    quiz_answers.router,
    prefix="/quiz-answers",
    tags=["Quiz Answers"],
    dependencies=[Depends(validate_secret_salt)]
)

app.include_router(
    quiz_questions.router,
    prefix="/quiz_questions",
    tags=["Quiz Questions"],
    dependencies=[Depends(validate_secret_salt)]
)

app.include_router(
    user_investor_profile.router,
    prefix="/user-investor-profile",
    tags=["User Investor Profile"],
    dependencies=[Depends(validate_secret_salt)]
)

app.include_router(
    investor_profiles.router,
    prefix="/investor_profiles",
    tags=["Investor Profiles"],
    dependencies=[Depends(validate_secret_salt)]
)

app.include_router(
    financial_advisors.router,
    prefix="/financial_advisors",
    tags=["Financial Advisors"]
)

app.include_router(
    questions.router,
    prefix="/questions",
    tags=["Questions"],
    dependencies=[Depends(decode_token)]
)

app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(decode_token)]
)

app.include_router(webhook.router)

app.include_router(
    config_router.router,
    dependencies=[Depends(decode_token)]
)

# Init DB and Start Watcher
logger.info("Initializing database...")
init_db()
logger.info("Database initialized successfully.")

start_env_watcher()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application with uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8000)