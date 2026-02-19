from fastapi import Query, HTTPException, Path, APIRouter, Depends
from sqlmodel import select
from typing import Annotated
from starlette import status
from app.models import *
from app.db import SessionDep
from app.routes.auth import get_current_user


public_tickets_router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"]
)

# Authentication is required via dependency injection
private_tickets_router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)]
)

@public_tickets_router.get("/", response_model=list[TicketPublic])
def read_tickets(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Ticket]:
    """Return a list of every Ticket.

    Args:
        offset (int): Allows you to skip the first 'n' Tickets.
        limit (int): Allows you to limit how many Tickets are returned.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        list[Ticket]: Returns up to 100 Tickets, or the limit via query parameters.

    Raises:
        None
    """
    
    tickets = session.exec(select(Ticket).offset(offset).limit(limit)).all()
    return tickets



@public_tickets_router.get("/search", response_model=list[TicketPublic])
def query_ticket_by_parameters(
    session: SessionDep,
    title: str | None = None,
    description: str | None = None,
    priority: int | None = Query(default=None, ge=1, le=5),
    status: TicketStatus | None = None,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[Ticket]:
    """Search for a Ticket via query parameters.

    Search for a Ticket by using its title, description, priority, or status.
    You can also combine any number of these query parameters.

    Args:
        title (str | None): The Ticket's title.
        description (str | None): The Ticket's description.
        priority (int | None): The Ticket's priority.
        status (TicketStatus | None): The Ticket's status.
        offset (int): Allows you to skip the first 'n' Tickets.
        limit (int): Allows you to limit how many Tickets are returned.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        list[Ticket]: A list of tickets that meet all the query parameters.

    Raises:
        HTTPException(404): If no Tickets were found that meet all the query parameters.
    """
    
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
            status_code=404, detail="The search query returned no results"
        )
        
    return tickets



@public_tickets_router.get("/{ticket_id}", response_model=TicketPublic)
def query_ticket_by_id(
    session: SessionDep,
    ticket_id: int = Path(gt=0)
) -> Ticket:
    """Returns a Ticket given its id.

    Args:
        ticket_id (int): The id of the Ticket to be returned.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        Ticket: Ticket with id == ticket_id.

    Raises:
        HTTPException(404): If no Ticket was found with id == ticket_id.
    """

    # Search using the ticket's id, which is the primary key in the DB
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket with {ticket_id=} does not exist"
        )
    
    return ticket



@private_tickets_router.post("/", response_model=TicketPublic, status_code=status.HTTP_201_CREATED)
def add_ticket(
    session: SessionDep,
    new_ticket: TicketCreate
) -> TicketPublic:
    """Add a Ticket to the database.

    Args:
        new_ticket (TicketCreate): The incoming JSON data from the user.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        TicketPublic: The Ticket that the user created.

    Raises:
        HTTPException(422): If the user did not provide data in all required fields.
    """

    title = new_ticket.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be blank")
    
    description = new_ticket.description.strip()
    if not description:
        raise HTTPException(status_code=422, detail="Description cannot be blank")
    
    ticket = Ticket(
        title=title,
        description=description,
        priority=new_ticket.priority,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket



@private_tickets_router.patch("/{ticket_id}", response_model=TicketPublic)
def update_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    session: SessionDep
) -> TicketPublic:
    """Update a Ticket in the database.

    Args:
        ticket_id (int): The id of the Ticket to be updated.
        ticket (TicketUpdate): The incoming JSON data from the user.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        TicketPublic: The Ticket that the user updated.

    Raises:
        HTTPException(422): If the user did not provide data in all required fields.
    """
    
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
@private_tickets_router.delete("/{ticket_id}", response_model=TicketPublic)
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