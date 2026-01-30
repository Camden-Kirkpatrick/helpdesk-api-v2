# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import *


app = FastAPI(
    title="Helpdesk API",
    version="1.0.0",
    description="A small REST API demonstrating CRUD + search + PATCH backed by SQLite."
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")



@app.get("/api/tickets")
def list_tickets():
    return [
        {"id": 1, "title": "Test ticket", "status": "open"}
    ]