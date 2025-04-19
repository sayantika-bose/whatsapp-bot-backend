import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services.auth_service import (
    login,
    logout,
    refresh_tokens,
    get_current_advisor,
    oauth2_scheme  # Import the scheme here
)
from models.database import get_db
from models.auth_model import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AdvisorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login_route(
    login_data: LoginRequest = Body(...),  # Changed from form to JSON body
    db: Session = Depends(get_db)
):
    """Authenticate user and return access/refresh tokens with advisor info."""
    try:
        tokens = login(db, login_data.email, login_data.password)  # Using login_data instead of form_data
        advisor_data = {
            "id": tokens["id"],
            "name": tokens["name"],
            "email": tokens["email"]
        }
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            advisor=AdvisorResponse(**advisor_data)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login route error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_route(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token and return advisor info."""
    try:
        new_tokens = refresh_tokens(request.refresh_token, db)
        
        # Get current advisor from the new token
        current_advisor = get_current_advisor(new_tokens["access_token"], db)
        advisor_data = {
            "id": current_advisor.id,
            "name": current_advisor.name,
            "email": current_advisor.email
        }
        
        return TokenResponse(
            access_token=new_tokens["access_token"],
            token_type=new_tokens["token_type"],
            advisor=AdvisorResponse(**advisor_data)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Refresh route error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout_route(
    current_advisor: AdvisorResponse = Depends(get_current_advisor),
    token: str = Depends(oauth2_scheme)
):
    """Revoke the current access token."""
    try:
        logout(token)
        return {"message": "Successfully logged out"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Logout route error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=AdvisorResponse)
async def get_current_user(
    current_advisor: AdvisorResponse = Depends(get_current_advisor)
):
    """Get current authenticated user details."""
    return current_advisor