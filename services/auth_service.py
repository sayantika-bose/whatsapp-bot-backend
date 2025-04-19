import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from models.database import FinancialAdvisor, get_db
from models.auth_model import TokenData

# Configure logger
logger = logging.getLogger(__name__)

# Token configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

security = HTTPBearer()

# Token blacklist (in production, use Redis or database)
token_blacklist = set()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Validate environment variables at startup
if not SECRET_KEY:
    logger.error("SECRET_KEY environment variable is not set")
    raise RuntimeError("SECRET_KEY environment variable is not set")

def hash_password(password: str) -> str:
    """Hash a password using Werkzeug's generate_password_hash."""
    try:
        logger.debug("Hashing password...")
        return generate_password_hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to hash password"
        )

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a provided password against a stored hash."""
    try:
        return check_password_hash(stored_password, provided_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_token_expiry(token_type: str) -> datetime:
    """Get token expiry based on type."""
    if token_type == "access":
        return datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError("Invalid token type")

def create_token(data: dict, token_type: str = "access") -> str:
    """Create a JWT token."""
    try:
        to_encode = data.copy()
        expire = get_token_expiry(token_type)
        logger.debug(f"Creating {token_type} token for data: {to_encode}")
        
        to_encode.update({
            "exp": expire,
            "type": token_type
        })
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Successfully created {token_type} token")
        return token
    except Exception as e:
        logger.error(f"Error creating {token_type} token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create {token_type} token"
        )

def create_access_token(data: dict) -> str:
    """Create an access token with standard expiration."""
    logger.debug(f"Creating access token for data: {data}")
    return create_token(data, token_type="access")

def create_refresh_token(data: dict) -> str:
    """Create a refresh token with longer expiration."""
    logger.debug(f"Creating refresh token for data: {data}")
    return create_token(data, token_type="refresh")

def decode_token(token: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Decode and verify a JWT token."""
    try:
        logger.debug("Starting token decode")
        if not token or not token.credentials:
            logger.debug("No token provided")
            raise JWTError("Missing token")
        logger.info(f"Token provided: {token}")
        token_str = token.credentials
        logger.debug(f"Token scheme: {token.scheme}")
        
        if len(token_str.split('.')) != 3:
            logger.debug("Invalid token format detected")
            raise JWTError(f"Invalid token format:{token_str}")

        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token decoded successfully. Type: {payload.get('type')}")
        
        if payload.get("type") not in ["access", "refresh"]:
            logger.debug(f"Invalid token type: {payload.get('type')}")
            raise JWTError("Invalid token type")
            
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_advisor(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> FinancialAdvisor:
    """Get the current authenticated advisor from the token."""
    try:
        # Check if token is blacklisted
        if token in token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked"
            )
            
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        advisor = db.query(FinancialAdvisor).filter_by(email=email).first()
        if advisor is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return advisor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def login(db: Session, email: str, password: str) -> dict:
    """Authenticate a financial advisor and return tokens."""
    try:
        logger.info(f"Attempting login for email: {email}")
        
        advisor = db.query(FinancialAdvisor).filter_by(email=email).first()
        if not advisor or not verify_password(advisor.password, password):
            logger.warning(f"Invalid credentials for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create tokens
        token_data = {"sub": advisor.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "id": advisor.id,
            "name": advisor.name,
            "email": advisor.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def logout(token: str = Depends(oauth2_scheme)) -> bool:
    """Add token to blacklist (logout)."""
    try:
        # Verify token first
        payload = decode_token(token)
        token_blacklist.add(token)
        logger.info(f"Token revoked for user: {payload.get('sub')}")
        return True
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

def refresh_tokens(refresh_token: str, db: Session) -> dict:
    """Generate new access token from refresh token."""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
            
        email = payload.get("sub")
        advisor = db.query(FinancialAdvisor).filter_by(email=email).first()
        if not advisor:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        new_access_token = create_access_token({"sub": email})
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )