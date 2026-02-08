from sqlmodel import Field, SQLModel
from enum import Enum


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
    id: int | None = Field(default=None, primary_key=True)

class TicketPublic(TicketBase):
    id: int

class TicketCreate(SQLModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5)

class TicketUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TicketStatus | None = None
