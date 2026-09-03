# Feature Descriptions

This document provides a deeper semantic explanation of the engineered features used in the ML models.

### `region_encoded`
To allow the XGBoost model to interpret the geographic regions, we applied label encoding. The integer mappings are defined in `feature_mapping.json`. Spatial adjacency is not preserved in this simple encoding, which is acceptable for tree-based models, though future iterations may move to geospatial embedding.

### `target`
The classification target. It is derived from the raw `severity` column. All events marked as "Severe" are mapped to `1`, while "Low", "Moderate", and "High" are mapped to `0`. This transforms the problem into a binary classification task: predicting severe, catastrophic events.

### `vulnerability_index` (Future/Planned)
A composite score that we plan to generate by combining `population.csv` (vulnerable population ratio) and `hospital_resources.csv` (ICU beds per capita). This will represent the human risk factor in a given region.
