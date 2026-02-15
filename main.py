from fastapi import FastAPI, Query, Form, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import date
from sqlmodel import select
from typing import Annotated
from starlette import status
import auth
import tickets
from models import *
from auth import UserDep
from db import SessionDep, create_db_and_tables


app = FastAPI(
    title="Helpdesk API",
    version="1.0.0",
    description="A small REST API demonstrating CRUD backed by SQLite and SQLModel."
)

app.include_router(auth.router)
app.include_router(tickets.public_tickets_router)
app.include_router(tickets.private_tickets_router)
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


@app.get("/user", response_model=UserPublic)
def get_user(user: UserDep, session: SessionDep):
    db_user = session.get(User, user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user