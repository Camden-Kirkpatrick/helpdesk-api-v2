from sqlmodel import Field, SQLModel
from enum import Enum


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class Ticket(SQLModel):
    id: int
    title: str
    description: str
    priority: int = Field(ge=1, le=5)
    status: TicketStatus = TicketStatus.open