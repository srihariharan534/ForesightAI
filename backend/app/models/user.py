from sqlalchemy import Column, String, Boolean, DateTime
import uuid
import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="Viewer")
    status = Column(String, default="Active")
    hashed_password = Column(String, nullable=True) # Optional since this is a demo
    last_active = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
