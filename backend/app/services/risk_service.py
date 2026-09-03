from sqlalchemy.orm import Session
from app.models.risk import RiskZone
from app.schemas.risk import RiskZoneItem
from typing import List

class RiskService:
    def get_risk_zones(self, db: Session) -> List[RiskZoneItem]:
        zones_db = db.query(RiskZone).all()
        return [
            RiskZoneItem(
                id=z.id,
                label=z.label,
                center=[z.lat, z.lng],
                radius=z.radius,
                risk=z.risk
            ) for z in zones_db
        ]

risk_service = RiskService()
