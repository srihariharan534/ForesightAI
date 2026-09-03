from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class KPIResponse(BaseModel):
    totalModels: int
    activeSimulations: int
    systemHealth: float
    criticalAlerts: int
    predictionsLast24h: int
    avgConfidence: float

class ActivityFeedItem(BaseModel):
    id: str
    type: str
    message: str
    time: str # We'll format the datetime as "10 min ago" in the service
    status: str

class TrendDataItem(BaseModel):
    name: str
    predictions: int
    accuracy: float

class RiskDistributionItem(BaseModel):
    name: str
    value: int
    color: str

class DashboardResponse(BaseModel):
    kpis: KPIResponse
    activityFeed: List[ActivityFeedItem]
    trendData: List[TrendDataItem]
    riskDistribution: List[RiskDistributionItem]
    
    model_config = ConfigDict(from_attributes=True)
