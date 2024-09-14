from pydantic import BaseModel, EmailStr, constr, Field, AfterValidator
from uuid import UUID
from typing import List, Optional, Annotated
from datetime import datetime



class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6)

class ClientCreate(BaseModel):
    full_name: constr(min_length=1, max_length=100)
    phone_number: constr(min_length=10, max_length=15)

class MessageCreate(BaseModel):
    content: constr(min_length=1)
    client_id: UUID

class SentMessageCreate(BaseModel):
    content: constr(min_length=1)
    clients: list[UUID | Annotated[str, AfterValidator(lambda x: UUID(x))]] = []

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

class ClientResponse(BaseModel):
    id: UUID
    full_name: str
    phone_number: str

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: UUID
    content: str
    client: ClientResponse

    class Config:
        from_attributes = True


class TokenBlacklistSchema(BaseModel):
    id: str
    revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True