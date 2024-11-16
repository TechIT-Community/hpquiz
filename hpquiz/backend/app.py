from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .db import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create connection to Database
    app.db = Database(uri="mongodb://localhost:27017", db_name="hpquiz")
    print("Connected to database.")
    
    yield
    
    # Close after the application is done running
    app.db.client.close()

app = FastAPI(lifespan=lifespan)
db: Database = app.db

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the HP Quiz API"}

@app.get("/forms/get")
async def form(id: Optional[str], name: Optional[str]):
    if not id and not name:
        raise ValueError("Either 'id' or 'name' must be provided.")
    
    if id:
        # Retrieve form first and then questions
        form = db.find_one("forms", {"_id": id})
        questions = db.find("questions", {"form_id": id}, sort_key="index")
        
        form["questions"] = questions
        
    elif name:
        # Retrieve form first and then questions
        form = db.find_one("forms", {"name": name})
        questions = db.find("questions", {"form_id": form["_id"]}, sort_key="index")
        
        form["questions"] = questions
        
    return form
        
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)