"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr


class SignupIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None

    class Config:
        from_attributes = True
