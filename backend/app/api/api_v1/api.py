from fastapi import APIRouter
from app.api.api_v1.endpoints import predict, dashboard, risk, simulation, users, train, mlops

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(predict.router, prefix="/predict", tags=["predictions"])
api_router.include_router(simulation.router, prefix="/simulate", tags=["simulations"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(train.router, prefix="/train", tags=["training"])
api_router.include_router(mlops.router, prefix="/mlops", tags=["mlops"])
