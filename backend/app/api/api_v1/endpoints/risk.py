from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.risk import RiskZoneItem
from app.services.risk_service import risk_service
from typing import List

router = APIRouter()

@router.get("/zones", response_model=List[RiskZoneItem])
def get_risk_zones(db: Session = Depends(get_db)):
    """
    Retrieve active geospatial risk zones.
    """
    return risk_service.get_risk_zones(db)
