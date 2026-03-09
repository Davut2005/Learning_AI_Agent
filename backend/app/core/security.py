"""Password hashing and JWT token handling."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from core.config import settings

ALGORITHM = "HS256"
# bcrypt truncates at 72 bytes; we truncate before hashing so hash is deterministic
BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_password_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: int) -> str:
    """Create JWT with user id as subject. subject is typically user.id."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Decode JWT and return user id (sub). Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (JWTError, ValueError):
        return None
