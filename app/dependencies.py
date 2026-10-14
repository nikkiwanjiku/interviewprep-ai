from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_token
from app.database import get_db
from app.models.user import User


# ==========================================================
# HTTP AUTHENTICATION
# ==========================================================

security = HTTPBearer()


# ==========================================================
# GET CURRENT AUTHENTICATED USER
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # ------------------------------------------------------
    # Get token from Authorization header
    # ------------------------------------------------------

    token = credentials.credentials

    # ------------------------------------------------------
    # Verify JWT
    # ------------------------------------------------------

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # ------------------------------------------------------
    # Get user email from JWT
    # ------------------------------------------------------

    email = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload."
        )

    # ------------------------------------------------------
    # Find user in database
    # ------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # ------------------------------------------------------
    # User does not exist
    # ------------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    # ------------------------------------------------------
    # Return actual User database object
    # ------------------------------------------------------

    return user