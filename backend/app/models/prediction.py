from sqlalchemy import Column, String, Float, JSON, DateTime
import uuid
import datetime
from app.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    input_features = Column(JSON, nullable=False)
    predicted_outcome = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    shap_values = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
