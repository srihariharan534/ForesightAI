from sqlalchemy.orm import Session
from app.models.dashboard import KPI, ActivityFeed, TrendData, RiskDistribution
from app.schemas.dashboard import DashboardResponse, KPIResponse, ActivityFeedItem, TrendDataItem, RiskDistributionItem

class DashboardService:
    def get_dashboard_data(self, db: Session) -> DashboardResponse:
        kpi_db = db.query(KPI).first()
        activities_db = db.query(ActivityFeed).order_by(ActivityFeed.created_at.desc()).limit(10).all()
        trend_db = db.query(TrendData).order_by(TrendData.date).all()
        risk_db = db.query(RiskDistribution).all()
        
        # If no data exists, return empty or default
        if not kpi_db:
            kpi = KPIResponse(
                totalModels=0, activeSimulations=0, systemHealth=0.0,
                criticalAlerts=0, predictionsLast24h=0, avgConfidence=0.0
            )
        else:
            kpi = KPIResponse(
                totalModels=kpi_db.total_models,
                activeSimulations=kpi_db.active_simulations,
                systemHealth=kpi_db.system_health,
                criticalAlerts=kpi_db.critical_alerts,
                predictionsLast24h=kpi_db.predictions_last_24h,
                avgConfidence=kpi_db.avg_confidence
            )
            
        activities = [
            ActivityFeedItem(
                id=a.id,
                type=a.type,
                message=a.message,
                time="Just now", # Ideally calculate delta from created_at
                status=a.status
            ) for a in activities_db
        ]
        
        trends = [
            TrendDataItem(name=t.name, predictions=t.predictions, accuracy=t.accuracy)
            for t in trend_db
        ]
        
        risks = [
            RiskDistributionItem(name=r.name, value=r.value, color=r.color)
            for r in risk_db
        ]
        
        return DashboardResponse(
            kpis=kpi,
            activityFeed=activities,
            trendData=trends,
            riskDistribution=risks
        )

dashboard_service = DashboardService()
