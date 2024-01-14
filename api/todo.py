from fastapi import Depends, FastAPI, HTTPException,Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional
from fastapi import Path
conn_str: str = (
    f"postgresql://Ch-Saqib:4H0iLkyNBpqu@ep-weathered-credit-48841962.us-east-2.aws.neon.tech/piaic?sslmode=require")

engine = create_engine(conn_str)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)

class TodoCreate(BaseModel):
    name: str

class TodoResponse(BaseModel):
    id: int
    name: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# CORS Configuration
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_all(db: Session = Depends(get_db)):
    return db.query(Todo).all()



@app.post("/api/", response_model=TodoResponse)
def add_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = Todo(name=todo.name)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.delete("/api/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(existing_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.put("/api/{todo_id}")
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    existing_todo.name = todo.name # type: ignore

    db.commit()
    db.refresh(existing_todo)

    return existing_todo