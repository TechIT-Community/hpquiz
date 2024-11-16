from typing import Optional
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Database
from pydantic import BaseModel

class FormInternal(BaseModel):
    title: str
    description: str
    author: str

    class Config:
        populate_by_name = True
     
class Option(BaseModel):
    option: str
    is_correct: bool
        
class QuestionInternal(BaseModel):  
    index: int
    question: str
    type: str
    options: list[Option]

    class Config:
        populate_by_name = True
        
        

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create connection to Database
    app.db = Database(uri="mongodb://localhost:27017", db_name="hpquiz")
    print("Connected to database.")
    
    yield
    
    # Close after the application is done running
    app.db.client.close()

app = FastAPI(lifespan=lifespan)
# app = FastAPI()
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

@app.post("/forms/create")
async def create_form(form_data: FormInternal):
    # Make _id None to let MongoDB generate a new ObjectId
    form_data.id = None
    form = db.insert_one("forms", form_data.model_dump())
    return form

@app.post("/forms/create/question")
async def create_question(form_id: str, question_data: list[QuestionInternal]):
    data = [{**question.model_dump(), "form_id": form_id} for question in question_data]
    db.insert_many("questions", data)
    
    return {"message": "Questions created successfully."}