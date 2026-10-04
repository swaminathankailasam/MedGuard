import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from database import get_db, Doctor

app = FastAPI(title="MEDGUARD AI Backend", version="1.0.0")

# Allow requests from the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DoctorCreate(BaseModel):
    username: str
    password: str

class DoctorLogin(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/register")
def register_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    db_user = db.query(Doctor).filter(Doctor.username == doctor.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_pw = get_password_hash(doctor.password)
    new_doctor = Doctor(username=doctor.username, password_hash=hashed_pw)
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return {"status": "success", "username": new_doctor.username}

@app.post("/login")
def login_doctor(doctor: DoctorLogin, db: Session = Depends(get_db)):
    db_user = db.query(Doctor).filter(Doctor.username == doctor.username).first()
    
    if not db_user or not verify_password(doctor.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
        
    return {"status": "success", "username": db_user.username, "message": "Successfully authenticated"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
