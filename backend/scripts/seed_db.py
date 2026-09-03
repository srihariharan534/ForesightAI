import sys
import os

# Add the project root to the python path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import SessionLocal, Base, engine
from app.models.dashboard import KPI, ActivityFeed, TrendData, RiskDistribution
from app.models.user import User
from app.models.risk import RiskZone
import app.models # To register all models

def seed_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding database...")
        
        # 1. KPI
        if not db.query(KPI).first():
            kpi = KPI(
                total_models=24,
                active_simulations=8,
                system_health=98.4,
                critical_alerts=2,
                predictions_last_24h=14502,
                avg_confidence=94.2
            )
            db.add(kpi)
            
        # 2. Activity Feed
        if not db.query(ActivityFeed).first():
            activities = [
                ActivityFeed(type='alert', message='Risk threshold exceeded in region EU-West', status='critical'),
                ActivityFeed(type='success', message='Model "Demand-Forecast-v2" deployed successfully', status='success'),
                ActivityFeed(type='info', message='User "Jane Doe" initiated a new simulation', status='info'),
                ActivityFeed(type='warning', message='API rate limit warning (90% usage)', status='warning'),
            ]
            db.add_all(activities)

        # 3. Trend Data
        if not db.query(TrendData).first():
            trends = [
                TrendData(name='Mon', predictions=4000, accuracy=92),
                TrendData(name='Tue', predictions=3000, accuracy=91),
                TrendData(name='Wed', predictions=2000, accuracy=93),
                TrendData(name='Thu', predictions=2780, accuracy=95),
                TrendData(name='Fri', predictions=1890, accuracy=96),
                TrendData(name='Sat', predictions=2390, accuracy=94),
                TrendData(name='Sun', predictions=3490, accuracy=94),
            ]
            db.add_all(trends)

        # 4. Risk Distribution
        if not db.query(RiskDistribution).first():
            risks = [
                RiskDistribution(name='Low Risk', value=400, color='#22C55E'),
                RiskDistribution(name='Medium Risk', value=300, color='#F59E0B'),
                RiskDistribution(name='High Risk', value=300, color='#EF4444'),
                RiskDistribution(name='Unknown', value=100, color='#64748B'),
            ]
            db.add_all(risks)
            
        # 5. Users
        if not db.query(User).first():
            users = [
                User(name='Alice Smith', email='alice@foresight.ai', role='Admin', status='Active'),
                User(name='Bob Johnson', email='bob@foresight.ai', role='Analyst', status='Active'),
                User(name='Carol Williams', email='carol@foresight.ai', role='Viewer', status='Inactive'),
                User(name='David Brown', email='david@foresight.ai', role='Engineer', status='Active'),
            ]
            db.add_all(users)
            
        # 6. Risk Zones
        if not db.query(RiskZone).first():
            zones = [
                RiskZone(label='Financial District', lat=40.7128, lng=-74.0060, radius=2000, risk='high'),
                RiskZone(label='Times Square', lat=40.7580, lng=-73.9855, radius=1500, risk='medium'),
                RiskZone(label='Central Park Area', lat=40.7829, lng=-73.9654, radius=3000, risk='low'),
            ]
            db.add_all(zones)

        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
