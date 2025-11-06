"""
Authentication API endpoints.
Handles user login, logout, token refresh, and current user info.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models.user import User
from app.schemas.user import UserLogin, Token, UserResponse, TokenData

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP bearer token credentials
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint - authenticate user and return JWT tokens.

    Args:
        user_credentials: Username and password
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh token endpoint - generate new access token from refresh token.

    Args:
        credentials: HTTP bearer token credentials (refresh token)
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value
    }

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        Current user information
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Logout endpoint.
    Since we're using JWT tokens, logout is handled client-side by deleting the tokens.
    This endpoint is here for API completeness and could be extended with token blacklisting.

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
