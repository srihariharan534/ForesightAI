from pydantic import BaseModel, ConfigDict
from typing import List

class RiskZoneItem(BaseModel):
    id: str
    label: str
    center: List[float] # [lat, lng]
    radius: int
    risk: str
    
    model_config = ConfigDict(from_attributes=True)
