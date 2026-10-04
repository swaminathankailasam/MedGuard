from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# 1. Create the Database Engine
DB_PATH = "sqlite:///./medguard.db"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})

# 2. Initialize the Base Class
Base = declarative_base()

# 3. Define the User (Doctor) Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    hospital_name = Column(String, nullable=True)
    role = Column(String, default="doctor")
    
    queries = relationship("QueryHistory", back_populates="doctor")

# 4. Define the Search History Table
class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    drug_a = Column(String, nullable=False)
    drug_b = Column(String, nullable=False)
    severity_result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("User", back_populates="queries")

# 5. Create the Tables
if __name__ == "__main__":
    print("⚙️ Initializing Secure SQLite Database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

# 6. Setup Session Maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()