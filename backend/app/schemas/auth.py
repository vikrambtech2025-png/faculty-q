from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    roles: List[str] = []
    is_active: bool

    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    refresh_token: str