from sqlmodel import Session, SQLModel, create_engine
from fastapi import Depends
from typing import Annotated

sqlite_file_name = "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# SessionDep is a type alias that tells FastAPI:
# "When a route asks for a SessionDep, create a database Session
# using get_session(), inject it into the function, and automatically
# close it after the request finishes.
SessionDep = Annotated[Session, Depends(get_session)]