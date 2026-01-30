# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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


app = FastAPI(
    title="Helpdesk API",
    version="1.0.0",
    description="A small REST API demonstrating CRUD + search + PATCH backed by SQLite."
)

app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def root():
    return {
        "service": "helpdesk-api",
        "status": "ok",
        "docs": "/docs"
    }


@app.get("/api/tickets")
def list_tickets():
    return [
        {"id": 1, "title": "Test ticket", "status": "open"}
    ]