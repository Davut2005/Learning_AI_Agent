"""Signup, login, and current user (JWT)."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas.auth import LoginIn, SignupIn, TokenOut, UserOut
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_session),
) -> User:
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/signup", response_model=TokenOut)
def signup(
    body: SignupIn,
    db: Session = Depends(get_session),
) -> TokenOut:
    """Register a new user. Returns JWT."""
    existing = db.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name[:255] if body.full_name else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(
    body: LoginIn,
    db: Session = Depends(get_session),
) -> TokenOut:
    """Authenticate and return JWT."""
    user = db.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account inactive")
    token = create_access_token(user.id)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Return current user from JWT. Requires Authorization: Bearer <token>."""
    return UserOut.model_validate(current_user)
