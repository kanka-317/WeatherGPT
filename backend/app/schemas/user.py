from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserSignUp(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: str = Field(..., min_length=5, max_length=255, description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="Plaintext password to hash")
    role: Optional[str] = Field(default="citizen", description="Role: citizen, disaster_officer, researcher")
    preferred_language: Optional[str] = Field(default="en", description="Preferred language code: en, bn, hi")


class UserSignIn(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, description="Registered email address")
    password: str = Field(..., min_length=1, description="Password to verify")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    preferred_language: str
    created_at: datetime
    token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]
