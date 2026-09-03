from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
import uuid
import datetime
from app.core.database import Base

class KPI(Base):
    __tablename__ = "kpis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    total_models = Column(Integer, default=0)
    active_simulations = Column(Integer, default=0)
    system_health = Column(Float, default=100.0)
    critical_alerts = Column(Integer, default=0)
    predictions_last_24h = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ActivityFeed(Base):
    __tablename__ = "activity_feed"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False) # alert, success, info, warning
    message = Column(String, nullable=False)
    status = Column(String, nullable=False) # critical, success, info, warning
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TrendData(Base):
    __tablename__ = "trend_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False) # e.g. Mon, Tue
    predictions = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    date = Column(DateTime, default=datetime.datetime.utcnow)

class RiskDistribution(Base):
    __tablename__ = "risk_distribution"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    value = Column(Integer, default=0)
    color = Column(String, nullable=False)
