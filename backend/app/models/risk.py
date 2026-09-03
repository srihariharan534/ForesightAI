from sqlalchemy import Column, String, Float, Integer
import uuid
from app.core.database import Base

class RiskZone(Base):
    __tablename__ = "risk_zones"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius = Column(Integer, default=1000)
    risk = Column(String, default="low") # high, medium, low
