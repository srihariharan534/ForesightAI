import os
import json
import random
import datetime
import pandas as pd
import numpy as np

# Ensure directories exist
dirs = [
    "datasets/raw",
    "datasets/cleaned",
    "datasets/processed",
    "datasets/sample",
    "datasets/external",
    "datasets/metadata"
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------
# 1. RAW DATASETS
# ---------------------------------------------------------
def generate_raw_data():
    np.random.seed(42)
    random.seed(42)
    
    n_records = 300
    base_time = datetime.datetime(2026, 1, 1)
    
    # hospital_resources.csv
    hospitals = []
    for i in range(n_records):
        hospitals.append({
            "hospital_id": f"HSP-{1000+i}",
            "name": f"Hospital {i+1}",
            "lat": 28.0 + np.random.uniform(-1, 1),
            "lng": 77.0 + np.random.uniform(-1, 1),
            "total_beds": np.random.randint(50, 1000),
            "available_beds": np.random.randint(0, 500) if np.random.random() > 0.1 else np.nan,
            "icu_capacity": np.random.randint(10, 100),
            "ventilators": np.random.randint(5, 50),
            "last_updated": (base_time + datetime.timedelta(days=i%30, hours=np.random.randint(0,24))).isoformat()
        })
    pd.DataFrame(hospitals).to_csv("datasets/raw/hospital_resources.csv", index=False)

    # flood_history.csv
    floods = []
    for i in range(n_records):
        floods.append({
            "event_id": f"FLD-{2000+i}",
            "date": (base_time - datetime.timedelta(days=np.random.randint(0, 3650))).date().isoformat(),
            "region": random.choice(["North", "South", "East", "West", "Central"]),
            "water_level_meters": np.random.uniform(5.0, 15.0),
            "rainfall_mm": np.random.uniform(50.0, 400.0) if np.random.random() > 0.05 else np.nan,
            "damage_estimate_usd": np.random.uniform(10000, 5000000),
            "severity": random.choice(["Low", "Moderate", "High", "Severe"])
        })
    pd.DataFrame(floods).to_csv("datasets/raw/flood_history.csv", index=False)

    # weather_history.csv
    weather = []
    for i in range(n_records):
        weather.append({
            "record_id": f"WTH-{i}",
            "timestamp": (base_time - datetime.timedelta(days=i)).isoformat(),
            "temp_c": np.random.uniform(15.0, 45.0),
            "humidity_pct": np.random.uniform(30.0, 100.0),
            "precipitation_mm": np.random.uniform(0, 150) if np.random.random() > 0.1 else np.nan,
            "wind_speed_kmh": np.random.uniform(5.0, 120.0),
            "weather_condition": random.choice(["Sunny", "Cloudy", "Rain", "Thunderstorm", "Cyclone"])
        })
    pd.DataFrame(weather).to_csv("datasets/raw/weather_history.csv", index=False)

    # population.csv
    population = []
    for i in range(n_records):
        population.append({
            "ward_id": f"WRD-{i}",
            "ward_name": f"Ward {i}",
            "total_population": int(np.random.normal(50000, 15000)),
            "vulnerable_population": int(np.random.normal(5000, 2000)) if np.random.random() > 0.05 else np.nan,
            "density_per_sqkm": np.random.uniform(1000, 25000),
            "avg_income": np.random.uniform(100, 5000)
        })
    pd.DataFrame(population).to_csv("datasets/raw/population.csv", index=False)
    
    # infrastructure.csv
    infra = []
    for i in range(n_records):
        infra.append({
            "infra_id": f"INF-{i}",
            "type": random.choice(["Bridge", "Dam", "Road", "Power Station", "Water Treatment"]),
            "lat": 28.0 + np.random.uniform(-1, 1),
            "lng": 77.0 + np.random.uniform(-1, 1),
            "age_years": np.random.randint(1, 100),
            "maintenance_status": random.choice(["Good", "Fair", "Poor", "Critical"]) if np.random.random() > 0.05 else np.nan,
            "risk_score": np.random.uniform(0, 10)
        })
    pd.DataFrame(infra).to_csv("datasets/raw/infrastructure.csv", index=False)

    # emergency_calls.csv
    calls = []
    for i in range(n_records):
        calls.append({
            "call_id": f"CALL-{i}",
            "timestamp": (base_time + datetime.timedelta(days=i%30, minutes=np.random.randint(0,1440))).isoformat(),
            "caller_lat": 28.0 + np.random.uniform(-1, 1),
            "caller_lng": 77.0 + np.random.uniform(-1, 1),
            "issue_type": random.choice(["Medical", "Fire", "Flood Rescue", "Power Outage", "Accident"]),
            "priority": random.choice(["Low", "Medium", "High", "Critical"]),
            "resolved": random.choice([True, False]) if np.random.random() > 0.02 else np.nan
        })
    pd.DataFrame(calls).to_csv("datasets/raw/emergency_calls.csv", index=False)

# ---------------------------------------------------------
# 2. CLEANED DATASETS
# ---------------------------------------------------------
def generate_cleaned_data():
    for file in os.listdir("datasets/raw"):
        if file.endswith(".csv"):
            df = pd.read_csv(f"datasets/raw/{file}")
            # Drop duplicates
            df = df.drop_duplicates()
            # Handle missing values: numeric -> median, categorical -> mode
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
                else:
                    df[col] = df[col].fillna(df[col].median() if not pd.isna(df[col].median()) else 0)
            df.to_csv(f"datasets/cleaned/{file}", index=False)

# ---------------------------------------------------------
# 3. PROCESSED DATASETS
# ---------------------------------------------------------
def generate_processed_data():
    df = pd.read_csv("datasets/cleaned/flood_history.csv")
    
    # Feature engineering for a classification task (Predicting Severe floods)
    df['target'] = (df['severity'] == 'Severe').astype(int)
    
    # Encoding
    df['region_encoded'] = df['region'].astype('category').cat.codes
    
    features = ['water_level_meters', 'rainfall_mm', 'region_encoded']
    X = df[features]
    y = df['target']
    
    # Normalize features
    X_norm = (X - X.mean()) / X.std()
    
    # Split
    indices = np.random.permutation(len(X_norm))
    train_idx, val_idx, test_idx = indices[:200], indices[200:250], indices[250:]
    
    X_norm.iloc[train_idx].to_csv("datasets/processed/train.csv", index=False)
    X_norm.iloc[val_idx].to_csv("datasets/processed/validation.csv", index=False)
    X_norm.iloc[test_idx].to_csv("datasets/processed/test.csv", index=False)
    
    X_norm.to_csv("datasets/processed/features.csv", index=False)
    pd.DataFrame(y).to_csv("datasets/processed/target.csv", index=False)
    
    # JSONs
    feature_mapping = {
        "region": {
            "North": 0, "South": 1, "East": 2, "West": 3, "Central": 4
        }
    }
    with open("datasets/processed/feature_mapping.json", "w") as f:
        json.dump(feature_mapping, f, indent=2)
        
    scaler_metadata = {
        "water_level_meters": {"mean": float(X['water_level_meters'].mean()), "std": float(X['water_level_meters'].std())},
        "rainfall_mm": {"mean": float(X['rainfall_mm'].mean()), "std": float(X['rainfall_mm'].std())},
        "region_encoded": {"mean": float(X['region_encoded'].mean()), "std": float(X['region_encoded'].std())}
    }
    with open("datasets/processed/scaler_metadata.json", "w") as f:
        json.dump(scaler_metadata, f, indent=2)

# ---------------------------------------------------------
# 4. SAMPLE DATASETS
# ---------------------------------------------------------
def generate_sample_data():
    df_raw_flood = pd.read_csv("datasets/raw/flood_history.csv").head(20)
    df_raw_flood.to_csv("datasets/sample/sample_prediction.csv", index=False)
    
    df_dashboard = pd.DataFrame({
        "date": pd.date_range(start="2026-09-01", periods=20),
        "active_alerts": np.random.randint(0, 10, 20),
        "predictions_served": np.random.randint(100, 1000, 20)
    })
    df_dashboard.to_csv("datasets/sample/sample_dashboard.csv", index=False)
    
    df_sim = pd.DataFrame({
        "scenario": [f"Scenario_{i}" for i in range(20)],
        "probability_of_failure": np.random.uniform(0, 1, 20),
        "estimated_damage_usd": np.random.uniform(10000, 500000, 20)
    })
    df_sim.to_csv("datasets/sample/sample_simulation.csv", index=False)
    
    df_risk = pd.DataFrame({
        "zone_id": [f"Z-{i}" for i in range(20)],
        "risk_level": [random.choice(["Low", "Medium", "High", "Critical"]) for _ in range(20)],
        "population_affected": np.random.randint(100, 50000, 20)
    })
    df_risk.to_csv("datasets/sample/sample_risk.csv", index=False)
    
    df_users = pd.DataFrame({
        "user_id": [f"U-{i}" for i in range(20)],
        "role": [random.choice(["Admin", "Analyst", "Viewer"]) for _ in range(20)],
        "last_login": [datetime.datetime.now().isoformat() for _ in range(20)]
    })
    df_users.to_csv("datasets/sample/sample_users.csv", index=False)

# ---------------------------------------------------------
# 6. METADATA JSONS
# ---------------------------------------------------------
def generate_metadata_jsons():
    schema = {
        "datasets": {
            "flood_history": {
                "columns": ["event_id", "date", "region", "water_level_meters", "rainfall_mm", "damage_estimate_usd", "severity"]
            }
        }
    }
    with open("datasets/metadata/schema.json", "w") as f:
        json.dump(schema, f, indent=2)
        
    version = {
        "version": "1.0.0",
        "last_updated": datetime.datetime.now().isoformat(),
        "pipeline_run_id": "RUN-998877"
    }
    with open("datasets/metadata/version.json", "w") as f:
        json.dump(version, f, indent=2)
        
    stats = {
        "total_records": 1800,
        "missing_values_handled": 142,
        "features_processed": 10
    }
    with open("datasets/metadata/dataset_statistics.json", "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    generate_raw_data()
    generate_cleaned_data()
    generate_processed_data()
    generate_sample_data()
    generate_metadata_jsons()
    print("All datasets and JSONs generated successfully.")
