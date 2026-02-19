from sqlmodel import Field, SQLModel
from enum import Enum
from datetime import date
from typing import Annotated
from pydantic import StringConstraints

NonEmptyStr = Annotated[
    str,
    StringConstraints(min_length=1, strip_whitespace=True)
]

# Ticket Models

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class TicketBase(SQLModel):
    title: NonEmptyStr
    description: NonEmptyStr
    priority: int = Field(ge=1, le=5)
    status: TicketStatus = TicketStatus.open

class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    created: date = Field(default_factory=date.today) # date.today() is run every time a Ticket is created

class TicketPublic(TicketBase):
    id: int
    created: date

class TicketCreate(SQLModel):
    title: NonEmptyStr
    description: NonEmptyStr
    priority: int = Field(ge=1, le=5)

class TicketUpdate(SQLModel):
    title: NonEmptyStr | None = None
    description: NonEmptyStr | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TicketStatus | None = None



# User and Token Models

class Token(SQLModel):
    access_token: str
    token_type: str

class UserBase(SQLModel):
    username: NonEmptyStr

class User(UserBase, table=True):
    username: NonEmptyStr = Field(unique=True, index=True)
    id: int | None = Field(default=None, primary_key=True, index=True)
    hashed_password: str

class UserPublic(UserBase):
    id: int

class UserCreate(UserBase):
    password: NonEmptyStr