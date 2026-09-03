from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Retrieve aggregated dashboard data (KPIs, activities, trends, risk distribution).
    """
    return dashboard_service.get_dashboard_data(db)
