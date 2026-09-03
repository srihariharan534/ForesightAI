from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.prediction import PredictionCreate, PredictionResponse
from app.services.prediction_service import prediction_service
from app.core.database import get_db
from app.models.prediction import Prediction

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
def create_prediction(
    *,
    db: Session = Depends(get_db),
    prediction_in: PredictionCreate
):
    """
    Run ML inference on provided features and return prediction with SHAP values.
    """
    # 1. Run inference via ML Engine
    result = prediction_service.predict(prediction_in)
    
    # 2. Save to database
    db_obj = Prediction(
        input_features=prediction_in.features,
        predicted_outcome=result["predicted_outcome"],
        confidence_score=result["confidence_score"],
        shap_values=result["shap_values"]
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 3. Attach runtime explainability & recommendations to returned object
    db_obj.executive_summary = result.get("executive_summary")
    db_obj.recommendations = result.get("recommendations")
    db_obj.pdp_curves = result.get("pdp_curves")
    db_obj.calibration_curve = result.get("calibration_curve")

    return db_obj
