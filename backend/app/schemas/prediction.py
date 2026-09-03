from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
import datetime

class PredictionCreate(BaseModel):
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    id: str
    predicted_outcome: str
    confidence_score: float
    shap_values: Optional[Dict[str, Any]] = None
    executive_summary: Optional[Dict[str, Any]] = None
    recommendations: Optional[list] = None
    pdp_curves: Optional[list] = None
    calibration_curve: Optional[list] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
