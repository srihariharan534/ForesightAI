# External Data Sources

## 1. NASA Earth Observation Data (MODIS/VIIRS)
- **Usage**: Used to extract soil moisture index and vegetation density.
- **Contribution**: High soil moisture correlates strongly with increased flood severity in our XGBoost model.

## 2. OpenStreetMap (OSM)
- **Usage**: Extraction of road networks, building footprints, and critical infrastructure locations (hospitals, fire stations).
- **Contribution**: Forms the basis of our `infrastructure.csv` and routing algorithms for emergency response simulations.

## 3. World Health Organization (WHO)
- **Usage**: Baseline standards for hospital bed density and ICU capacity per 10,000 population.
- **Contribution**: Used to calculate the `vulnerability_index` in `population.csv`.

## 4. Indian Government Open Data (data.gov.in)
- **Usage**: Historical rainfall data, river basin water levels, and ward-level census data.
- **Contribution**: Ground truth for `weather_history.csv` and `population.csv`.

## 5. NOAA Global Historical Climatology Network (GHCN)
- **Usage**: Long-term climate trends and extreme weather event frequencies.
- **Contribution**: Used in the Scenario Engine to generate realistic extreme weather stress tests (e.g., "1-in-100 year rainfall").
