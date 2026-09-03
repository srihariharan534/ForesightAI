# Data Quality Report

**Pipeline Run:** RUN-998877
**Date Evaluated:** 2026-09-01

## 1. Completeness
- **Raw completeness**: 94.2% across all 6 raw datasets.
- **Cleaned completeness**: 100% (after automated median/mode imputation).
- **Missing Value Hotspots**: `available_beds` in hospitals (approx 10% missing), and `vulnerable_population` in population stats.

## 2. Uniqueness
- **Duplicates found**: 0 duplicate rows across all datasets.
- **ID Integrity**: 100% unique primary keys in all tables (`hospital_id`, `event_id`, etc.).

## 3. Validity
- **Ranges**:
  - `water_level_meters`: Valid (all between 5.0 and 15.0).
  - `temp_c`: Valid (all between 15.0 and 45.0).
  - `lat`/`lng`: Valid bounding box around New Delhi (27.0-29.0 N, 76.0-78.0 E).

## 4. Consistency
- **Timestamps**: All timestamps successfully parse to ISO-8601.
- **Categorical Constraints**: All regions map strictly to ["North", "South", "East", "West", "Central"].

**Conclusion**: The datasets meet the "Gold Standard" tier for ingestion into the ForesightAI ML training pipeline.
