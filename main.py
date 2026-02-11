# uvicorn main:app --reload

from fastapi import FastAPI, Query, Form, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import date
from sqlmodel import select
from models import *
from db import *



app = FastAPI(
    title="Helpdesk API",
    version="1.0.0",
    description="A small REST API demonstrating CRUD backed by SQLite and SQLModel."
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico", media_type="image/x-icon")

@app.get("/")
def index():
    return FileResponse("static/index.html")



# Get all Tickets
@app.get("/api/tickets/", response_model=list[TicketPublic])
def read_tickets(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Ticket]:
    
    tickets = session.exec(select(Ticket).offset(offset).limit(limit)).all()
    return tickets



# Search for a ticket via query parameters
@app.get("/api/tickets/search", response_model=list[TicketPublic])
def query_ticket_by_parameters(
    session: SessionDep,
    title: str | None = None,
    description: str | None = None,
    priority: int | None = Query(default=None, ge=1, le=5),
    status: TicketStatus | None = None,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[Ticket]:
    
    stmt = select(Ticket)

    if title is not None:
        stmt = stmt.where(Ticket.title.ilike(title))

    if description is not None:
        stmt = stmt.where(Ticket.description.ilike(description))

    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority)

    if status is not None:
        stmt = stmt.where(Ticket.status == status)

    tickets = session.exec(stmt.offset(offset).limit(limit)).all()

    if len(tickets) == 0:
        raise HTTPException(
            status_code=404, detail=f"The search query returned no results"
        )
        
    return tickets



# Get Ticket by id
@app.get("/api/tickets/{ticket_id}", response_model=TicketPublic)
def query_ticket_by_id(session: SessionDep, ticket_id: int = Path(gt=0)) -> Ticket:
    # Search using the ticket's id, which is the primary key in the DB
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )
    return ticket



# Add Ticket
@app.post("/api/tickets/", response_model=TicketPublic)
def add_ticket(
    session: SessionDep,
    title: str = Form(..., min_length=1),
    description: str = Form(..., min_length=1),
    priority: int = Form(..., ge=1, le=5),
) -> TicketPublic:

    title = title.strip()
    if not title:
        raise HTTPException(422, "Title cannot be blank")
    
    description = description.strip()
    if not description:
        raise HTTPException(422, "Description cannot be blank")
    
    ticket = Ticket(
        title=title,
        description=description,
        priority=priority,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket



# Update Ticket
@app.patch("/api/tickets/{ticket_id}", response_model=TicketPublic)
def update_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    session: SessionDep
) -> TicketPublic:
    
    db_ticket = session.get(Ticket, ticket_id)

    if not db_ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )
    
    if ticket.title is not None:
        if ticket.title.strip() != "":
            db_ticket.title = ticket.title
        else:
            raise HTTPException(
                status_code=422, detail=f"title cannot be empty"
            )
        
    if ticket.description is not None:
        if ticket.description.strip() != "":
            db_ticket.description = ticket.description
        else:
            raise HTTPException(
                status_code=422, detail=f"description cannot be empty"
            )

    if ticket.priority is not None:
        db_ticket.priority = ticket.priority
    if ticket.status is not None:
        db_ticket.status = ticket.status

    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket



# Delete Ticket
@app.delete("/api/tickets/{ticket_id}", response_model=TicketPublic)
def delete_ticket(
    ticket_id: int,
    session: SessionDep
) -> TicketPublic:
    
    db_ticket = session.get(Ticket, ticket_id)

    if not db_ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )

    session.delete(db_ticket)
    session.commit()
    return db_ticket