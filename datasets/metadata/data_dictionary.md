# Data Dictionary

Comprehensive data dictionary for the primary features used in ForesightAI's flood risk prediction model.

| Feature Name | Type | Range / Categories | Description | Unit | Missing Value Strategy |
|---|---|---|---|---|---|
| `water_level_meters` | Float | 0.0 - 25.0 | Peak water level recorded at the river monitoring station. | Meters | Median imputation |
| `rainfall_mm` | Float | 0.0 - 800.0 | Cumulative rainfall over a 24-hour rolling window. | Millimeters | Median imputation |
| `region` | Categorical | North, South, East, West, Central | Geographic zone of the event. | N/A | Mode imputation |
| `severity` | Categorical | Low, Moderate, High, Severe | Target variable representing the historical impact of the flood event. | N/A | Drop if missing |
| `damage_estimate_usd` | Float | 0 - 10B | Estimated economic damage caused by the event. | USD | Median imputation |
| `vulnerable_population`| Integer| 0 - 500,000 | Number of individuals in the affected zone lacking access to immediate high-ground or medical care. | People | Median imputation |
