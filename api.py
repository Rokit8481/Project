from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import os

app = FastAPI()

DB = "users.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

class UserBase(BaseModel):
    username: str
    email: str

class User(UserBase):
    id: int

@app.post("/create_user", response_model = User)
def create_user(user: UserBase):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (user.username, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return User(id = user_id, **user.dict())

@app.get("/users", response_model=List[User])
def get_all_users():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [User(id=row[0], username=row[1], email=row[2]) for row in rows]

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1], email=row[2])
    raise HTTPException(status_code=404, detail="User not found")