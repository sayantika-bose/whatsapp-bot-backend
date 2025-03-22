import logging
import os
from datetime import datetime, timezone, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import HTTPException, status
from models.database import FinancialAdvisor

# Configure logger
logger = logging.getLogger(__name__)

# Secret key and algorithm for JWT (with fallback for missing env vars)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default to HS256 if not set
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# Validate environment variables at startup
if not SECRET_KEY:
    logger.error("SECRET_KEY environment variable is not set")
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    logger.warning("ACCESS_TOKEN_EXPIRE_MINUTES not set, defaulting to 30")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
else:
    try:
        ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)
    except ValueError:
        logger.error("Invalid ACCESS_TOKEN_EXPIRE_MINUTES value, defaulting to 30")
        ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Hash a password using Werkzeug's generate_password_hash.
    """
    try:
        logger.debug("Hashing password...")
        hashed = generate_password_hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to hash password"
        )

def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a provided password against a stored hash.
    """
    try:
        logger.debug("Verifying password...")
        result = check_password_hash(stored_password, provided_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False  # Fail safely rather than raising an exception here

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token with an expiration time.
    """
    try:
        logger.debug("Creating access token...")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        
        if not SECRET_KEY or not ALGORITHM:
            logger.error("JWT configuration missing: SECRET_KEY or ALGORITHM not set")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation configuration error"
            )

        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Access token created with expiration: {expire}")
        return token
    except JWTError as e:
        logger.error(f"JWT encoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def login(db: Session, email: str, password: str):
    """
    Authenticate a financial advisor and return a JWT token on success.
    """
    try:
        logger.info(f"Attempting login for email: {email}")
        
        # Query the database for the advisor
        advisor = db.query(FinancialAdvisor).filter_by(email=email).first()
        
        if not advisor:
            logger.warning(f"No advisor found for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(advisor.password, password):
            logger.warning(f"Password verification failed for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Login successful for advisor ID: {advisor.id}")

        # Generate JWT token
        access_token = create_access_token({"sub": advisor.email})

        response = {
            "id": advisor.id,
            "name": advisor.name,
            "mobile_number": advisor.mobile_number,
            "email": advisor.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
        logger.debug(f"Login response prepared for email: {email}")
        return response

    except HTTPException as e:
        # Re-raise HTTPExceptions (e.g., 401 Unauthorized) as they are intentional
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during login for email {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"WWW-Authenticate": "Bearer"},
        )
