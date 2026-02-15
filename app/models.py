from sqlmodel import Field, SQLModel
from enum import Enum
from datetime import date


# Ticket Models

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class TicketBase(SQLModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5)
    status: TicketStatus = TicketStatus.open

class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    created: date = Field(default_factory=date.today)

class TicketPublic(TicketBase):
    id: int
    created: date

class TicketCreate(SQLModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5)

class TicketUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TicketStatus | None = None



# User and Token Models

class UserBase(SQLModel):
    username: str = Field(unique=True)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    hashed_password: str

class UserPublic(UserBase):
    id: int

class UserCreate(UserBase):
    password: str



class Token(SQLModel):
    access_token: str
    token_type: str