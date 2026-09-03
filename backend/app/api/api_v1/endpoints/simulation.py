from fastapi import APIRouter
from app.services.simulation_service import simulation_service
from typing import Dict, Any

router = APIRouter()

@router.post("/")
def run_simulation(params: Dict[str, Any]):
    """
    Run a what-if Monte Carlo simulation with the provided parameters.
    """
    return simulation_service.run_simulation(params)
