from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_connection

app = FastAPI()

class UserLogin(BaseModel):
    username: str
    password: str
    role: str 

@app.post("/login/")
def login(user: UserLogin):
    conn = create_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()

    # Determine the correct table based on role
    if user.role == "Patient":
        table_name = "patients"
    elif user.role == "Doctor":
        table_name = "doctors"
    elif user.role == "Admin":
        table_name = "admins"
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Store login details in MySQL
    try:
        cursor.execute(f"INSERT INTO {table_name} (username, password) VALUES (%s, %s)", (user.username, user.password))
        conn.commit()
        return {"message": f"User {user.username} stored in {table_name} table successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
