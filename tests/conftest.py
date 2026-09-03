"""Pytest configuration, fixtures, and shared test utilities for ForesightAI.

This conftest.py is auto-loaded by pytest and provides:
  - FastAPI test client
  - In-memory SQLite database with seeded test data
  - Sample loan feature fixtures
  - Mock ML model fixtures
  - Simulation engine fixtures

Run tests::

    pytest tests/ -v --tb=short --no-cov
    pytest tests/ -v --cov=backend --cov=ml_engine --cov=simulation --cov-report=term-missing
"""

import datetime
import uuid
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
from app.core.database import Base, get_db
from app.models.prediction import Prediction
from app.models.user import User
from app.models.risk import RiskZone
from app.models.dashboard import KPI, ActivityFeed, TrendData, RiskDistribution

# ---------------------------------------------------------------------------
# Test Database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_foresight.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create all tables in the test DB at session start, drop at end."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    # Clean up test DB file
    if os.path.exists("test_foresight.db"):
        try:
            os.remove("test_foresight.db")
        except OSError:
            pass


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a clean transactional database session per test.

    Each test runs in its own transaction which is rolled back at the end,
    ensuring test isolation without needing to recreate tables.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI test client with the test DB injected via dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def seeded_db(db_session: Session) -> Session:
    """Seed the test DB with realistic KPI, activity, trend, risk, and user data."""
    # KPI
    kpi = KPI(
        id=str(uuid.uuid4()),
        total_models=5,
        active_simulations=3,
        system_health=98.5,
        critical_alerts=1,
        predictions_last_24h=247,
        avg_confidence=0.91,
    )
    db_session.add(kpi)

    # Activity Feed
    activities = [
        ActivityFeed(
            id=str(uuid.uuid4()),
            type="success",
            message="Loan application #A1042 approved with 92% confidence.",
            status="success",
        ),
        ActivityFeed(
            id=str(uuid.uuid4()),
            type="alert",
            message="High-risk cluster detected in North region.",
            status="critical",
        ),
        ActivityFeed(
            id=str(uuid.uuid4()),
            type="info",
            message="Monthly model retraining scheduled for tomorrow.",
            status="info",
        ),
    ]
    db_session.add_all(activities)

    # Trend Data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        db_session.add(TrendData(
            id=str(uuid.uuid4()),
            name=day,
            predictions=80 + i * 12,
            accuracy=0.88 + i * 0.005,
        ))

    # Risk Distribution
    for name, val, col in [
        ("Low Risk", 55, "#22c55e"),
        ("Medium Risk", 30, "#eab308"),
        ("High Risk", 12, "#f97316"),
        ("Critical Risk", 3, "#ef4444"),
    ]:
        db_session.add(RiskDistribution(id=str(uuid.uuid4()), name=name, value=val, color=col))

    # Risk Zones
    for label, lat, lng, risk in [
        ("Downtown Financial Hub", 28.6139, 77.2090, "high"),
        ("North Industrial Zone",  28.7041, 77.1025, "medium"),
        ("South Residential Area", 28.5244, 77.1855, "low"),
        ("East Tech Corridor",     28.6280, 77.3743, "medium"),
    ]:
        db_session.add(RiskZone(
            id=str(uuid.uuid4()), label=label,
            lat=lat, lng=lng, radius=1500, risk=risk,
        ))

    # Users
    for name, email, role, status in [
        ("Alice Sharma",   "alice@foresightai.com",   "Admin",   "active"),
        ("Rajesh Patel",   "rajesh@foresightai.com",  "Analyst", "active"),
        ("Priya Nair",     "priya@foresightai.com",   "Viewer",  "inactive"),
    ]:
        db_session.add(User(
            id=str(uuid.uuid4()), name=name,
            email=email, role=role, status=status,
        ))

    # Predictions
    for outcome, conf in [("Approved", 0.93), ("Rejected", 0.78), ("Approved", 0.85)]:
        db_session.add(Prediction(
            id=str(uuid.uuid4()),
            input_features={"age": 35, "income": 62000.0, "credit_score": 720},
            predicted_outcome=outcome,
            confidence_score=conf,
            shap_values={"base_value": 0.5, "contributions": {"age": 0.1, "income": 0.25}},
        ))

    db_session.commit()
    return db_session


# ---------------------------------------------------------------------------
# ML / Feature fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_loan_features() -> Dict[str, Any]:
    """Standard low-risk loan feature dict."""
    return {
        "age": 35,
        "income": 65000.0,
        "credit_score": 720,
        "years_employed": 8,
        "loan_amount": 22000.0,
        "num_dependents": 2,
        "region": "North",
        "employment_type": "Full-Time",
        "education": "Bachelor",
        "has_previous_default": 0,
    }


@pytest.fixture
def high_risk_features() -> Dict[str, Any]:
    """High-risk loan feature dict (likely rejection)."""
    return {
        "age": 24,
        "income": 18000.0,
        "credit_score": 420,
        "years_employed": 1,
        "loan_amount": 45000.0,
        "num_dependents": 4,
        "region": "South",
        "employment_type": "Unemployed",
        "education": "None",
        "has_previous_default": 1,
    }


@pytest.fixture
def sample_portfolio() -> List[Dict[str, Any]]:
    """Small portfolio of 5 loans for portfolio tests."""
    return [
        {"age": 35, "income": 65000.0, "credit_score": 720, "loan_amount": 22000.0,
         "years_employed": 8, "has_previous_default": 0},
        {"age": 42, "income": 85000.0, "credit_score": 780, "loan_amount": 30000.0,
         "years_employed": 15, "has_previous_default": 0},
        {"age": 29, "income": 32000.0, "credit_score": 580, "loan_amount": 18000.0,
         "years_employed": 3, "has_previous_default": 0},
        {"age": 55, "income": 120000.0, "credit_score": 810, "loan_amount": 50000.0,
         "years_employed": 25, "has_previous_default": 0},
        {"age": 27, "income": 25000.0, "credit_score": 490, "loan_amount": 35000.0,
         "years_employed": 2, "has_previous_default": 1},
    ]


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """100-row DataFrame for ML unit tests."""
    rng = np.random.default_rng(42)
    n = 100
    return pd.DataFrame({
        "age": rng.integers(18, 70, n),
        "income": rng.normal(55000, 10000, n).clip(10000, 150000),
        "credit_score": rng.integers(300, 850, n),
        "employment_type": rng.choice(["Full-Time", "Part-Time", "Self-Employed"], n),
        "region": rng.choice(["North", "South", "East", "West"], n),
        "target": rng.integers(0, 2, n),
    })
