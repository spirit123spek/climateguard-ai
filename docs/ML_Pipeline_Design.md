# ML Pipeline Design

ClimateGuard AI uses machine learning to convert real environmental data into climate risk predictions, simulator outputs, alert signals, and ESG-aware sustainability insights.

This document is a design artifact only. It does not train models, write Python, create notebooks, generate synthetic data, or create model artifacts.

## ML Principles

1. All model inputs must originate from real live APIs, historical datasets, validated Supabase records, or clearly labeled user scenario inputs.
2. No fake, static, placeholder, or hardcoded climate values may be used for training, evaluation, prediction, simulation, ESG scoring, or reports.
3. Every prediction must preserve source data references, model version, input features, prediction timestamp, and confidence where available.
4. Simulation inputs are user-defined scenario variables and must never be stored as observed climate readings.
5. ESG and sustainability outputs must be calculated from real environmental inputs and documented scoring logic.

## Pipeline Overview

```text
Candidate Datasets and Live Records
  AQI India Dataset
  Air Quality Dataset
  NASA EarthData references
  Historical Weather Datasets
  Stored OpenWeather readings
  Stored AQICN readings
        |
        v
Data Validation
  Source verification
  Unit checks
  Timestamp checks
  Location normalization
  Missing-value review
        |
        v
Feature Engineering
  Pollutant features
  Weather features
  Time features
  Trend features
  Rolling averages
  Risk labels
        |
        v
Training Pipeline
  Train/validation/test split
  Class balance review
  Baseline model
  Random Forest Classifier
  Model evaluation
  Model versioning
        |
        v
Inference Pipeline
  Live prediction
  Scenario simulation
  ESG score interaction
  Alert index generation
        |
        v
Supabase Storage
  predictions
  simulations
  reports
  audit_logs
```

## Candidate Datasets

| Dataset | Dataset Purpose | Features Available | Data Quality Concerns | Missing Values Strategy |
| --- | --- | --- | --- | --- |
| AQI India Dataset | Train and validate air-pollution-driven risk classification for Indian cities | AQI, PM2.5, PM10, station/city, timestamp, pollutant readings where available | Station coverage may vary by city; pollutant units and AQI scale must be verified; timestamps may be irregular | Preserve missing pollutant fields as null during raw ingestion; impute only during model training with documented strategy; exclude rows with missing target labels |
| Air Quality Dataset | Broaden pollution feature coverage and historical AQI trends | AQI, PM2.5, PM10, NO2, SO2, CO, O3, station metadata, timestamp | Different providers may use different measurement units, station naming, and reporting intervals | Normalize units first; add missingness indicators for key pollutants; use median or model-safe imputation only after train/test split |
| NASA EarthData references | Add satellite-supported and climate context for historical environmental baselines | Temperature-related variables, rainfall or precipitation indicators, atmospheric indicators, geospatial and temporal metadata depending on selected product | Dataset products vary by spatial resolution, temporal resolution, access format, and coverage; product selection must be finalized before implementation | Resample to the project time grain; mark unavailable fields as null; avoid interpolating large gaps without documenting assumptions |
| Historical Weather Datasets | Train weather-aware risk prediction and trend analysis | Temperature, humidity, rainfall, wind speed, atmospheric conditions, timestamp, city or coordinates | Inconsistent city names, missing rainfall, different units, and station changes over time | Normalize locations and units; distinguish source-confirmed zero rainfall from missing rainfall; impute weather features only with documented train-only statistics |
| Stored OpenWeather API readings | Support live inference, recent trend features, and model monitoring | Temperature, humidity, rainfall, wind speed, weather condition, source timestamp, city, coordinates | Live API outages, missing precipitation fields, stale observations | Use latest valid reading only when freshness rules pass; otherwise return unavailable or stale-with-timestamp status |
| Stored AQICN API readings | Support live AQI inference, recent air quality trends, and model monitoring | AQI, PM2.5, PM10, additional pollutant metrics, station, source timestamp, city | Station availability differs by city; pollutant values may be partial | Use available source values; do not invent missing pollutants; add missingness flags for inference if the trained model supports them |

## Dataset Selection Rules

1. Prefer datasets with clear source ownership, timestamp, location, units, and licensing.
2. Training datasets must be versioned by source, date range, import date, and preprocessing version.
3. Rows used for training must be traceable back to source records or imported dataset references.
4. Datasets with unresolved unit ambiguity should be quarantined until corrected.
5. Historical datasets should not be mixed with live readings until both are normalized to the same feature contract.

## Model Inputs

The initial model input contract should match the project context and backend prediction contract.

| Input Feature | Source | Type | Required For Initial Model | Notes |
| --- | --- | --- | --- | --- |
| `aqi` | AQICN API, AQI India Dataset, Air Quality Dataset | Numeric | Yes | Primary air quality risk signal |
| `pm25` | AQICN API, AQI India Dataset, Air Quality Dataset | Numeric | Yes | Fine particulate pollution |
| `pm10` | AQICN API, AQI India Dataset, Air Quality Dataset | Numeric | Yes | Coarse particulate pollution |
| `temperature` | OpenWeather API, NASA EarthData references, Historical Weather Datasets | Numeric | Yes | Normalize to Celsius unless the system standard changes |
| `humidity` | OpenWeather API, Historical Weather Datasets | Numeric | Yes | Percentage from 0 to 100 |
| `rainfall` | OpenWeather API, NASA EarthData references, Historical Weather Datasets | Numeric | Yes | Preserve missing versus source-confirmed zero |
| `wind_speed` | OpenWeather API, Historical Weather Datasets | Numeric | Yes | Normalize to a single unit |
| `city` | Source metadata and user selection | Categorical | Optional | May be used for monitoring or future location-aware models |
| `latitude` | Source metadata | Numeric | Optional | Useful for geospatial model extensions |
| `longitude` | Source metadata | Numeric | Optional | Useful for geospatial model extensions |
| `recorded_at` | Source timestamp | Datetime | Optional derived features | Used to derive hour, day, month, and season |

## Prediction Outputs

| Output | Type | Description | Storage Target |
| --- | --- | --- | --- |
| `risk_category` | Classification label | Low Risk, Moderate Risk, High Risk, or Severe Risk | `predictions.risk_category` |
| `risk_score` | Numeric score | Calibrated or normalized numeric climate risk score | `predictions.risk_score` |
| `confidence_score` | Numeric score | Model confidence or calibrated probability where available | `predictions.confidence_score` |
| `alert_index` | Derived label | Green, Yellow, Orange, or Red alert classification based on risk output and thresholds | `predictions.alert_index` |
| `escalation_estimate` | Structured metadata | Optional estimate of risk movement based on trends and model outputs | `predictions.escalation_estimate` |

Initial risk classes:

* Low Risk
* Moderate Risk
* High Risk
* Severe Risk

## Target Label Strategy

The training target must be derived from documented real environmental thresholds or verified historical labels. If no reliable labeled dataset exists, the first supervised model should use a transparent label generation policy based on accepted environmental standards and source values, and the policy must be documented before training.

Potential label inputs:

* AQI severity bands from the selected AQI standard.
* PM2.5 and PM10 severity thresholds from the selected air quality standard.
* Weather stress indicators such as high temperature, heavy rainfall, high humidity, and high wind speed.
* Historical incident or alert labels only if a real dataset is available and properly licensed.

No label may be invented manually for demonstration.

## Feature Engineering Strategy

### Core Numeric Features

Use normalized numeric values for AQI, PM2.5, PM10, temperature, humidity, rainfall, and wind speed.

### Missingness Indicators

Create explicit binary indicators for important missing fields, such as:

* `is_pm25_missing`
* `is_pm10_missing`
* `is_rainfall_missing`
* `is_wind_speed_missing`

This helps the model distinguish missing source data from low or zero values.

### Rolling And Trend Features

When historical data is available for a city, calculate features such as:

* 24-hour AQI average
* 7-day AQI average
* 7-day temperature average
* 7-day rainfall total
* PM2.5 rolling average
* PM10 rolling average
* AQI change versus previous period
* Temperature anomaly versus historical baseline

Rolling features must use only past and current data relative to the prediction timestamp to avoid data leakage.

### Time Features

Derive from source timestamp:

* Hour of day
* Day of week
* Month
* Season

Time features should be used carefully because seasonal patterns may differ by geography.

### Location Features

Initial model should avoid overfitting to city names if training data is small. Future versions may include:

* City encoding
* Region encoding
* Latitude and longitude
* Climate zone

### Feature Scaling

Random Forest models do not require strict scaling, but all units must be normalized. If future models require scaling, scalers must be fitted on training data only and versioned with the model artifact.

## Missing Values Strategy

| Missing Field Type | Strategy |
| --- | --- |
| Missing target label | Exclude from supervised training until label can be derived or verified |
| Missing AQI | Exclude from initial model training if AQI is required; future models may support fallback pollutant-only inference |
| Missing PM2.5 or PM10 | Use documented imputation after train/test split and add missingness indicators |
| Missing rainfall | Distinguish unavailable from confirmed zero; impute only if required by model and document method |
| Missing weather feature | Use train-only median imputation or source-specific fallback if documented |
| Missing city or timestamp | Quarantine row because traceability and time-based validation are compromised |
| Live inference missing feature | Return unavailable if required features are absent, unless the active model version explicitly supports missingness |

## Training Pipeline

```text
Dataset registration
-> Raw data ingestion
-> Source and license verification
-> Schema validation
-> Unit normalization
-> Location normalization
-> Timestamp normalization
-> Target label creation or verification
-> Train/validation/test split
-> Missing value handling fitted on train split only
-> Feature engineering
-> Baseline model training
-> Random Forest Classifier training
-> Evaluation and threshold review
-> Model calibration review
-> Model artifact versioning
-> Documentation of data, features, metrics, and limitations
-> Approval for backend integration
```

### Initial Model

The initial production candidate is a Random Forest Classifier.

Reasons:

* Handles nonlinear relationships between pollution and weather features.
* Works well with tabular environmental datasets.
* Provides feature importance for explainability.
* Does not require heavy preprocessing compared with neural models.

### Future Model Candidates

Future versions may evaluate:

* Gradient boosting models for stronger tabular performance.
* Time-series forecasting models for trend-aware predictions.
* Calibrated classifiers for more reliable confidence scores.
* City-specific or region-specific models if enough data is available.

## Evaluation Metrics

| Metric | Purpose |
| --- | --- |
| Accuracy | General classification performance across all classes |
| Macro F1 Score | Balanced performance across Low, Moderate, High, and Severe risk classes |
| Weighted F1 Score | Accounts for class imbalance while preserving overall quality |
| Precision per class | Measures false alert risk, especially for High and Severe classes |
| Recall per class | Measures missed-risk risk, especially for High and Severe classes |
| Confusion matrix | Shows which risk classes are confused with each other |
| ROC-AUC or PR-AUC | Useful if probability outputs are available and class framing supports it |
| Calibration error | Checks whether confidence scores are reliable |
| Feature importance review | Confirms model behavior is plausible and not dominated by leakage |

Minimum evaluation expectations before production use:

1. Report metrics for every risk class.
2. Specifically review Severe Risk recall.
3. Check class imbalance and minority-class performance.
4. Validate on time-separated data when possible.
5. Compare against a simple baseline threshold model.

## Model Validation And Leakage Controls

* Split data by time where possible to simulate future prediction behavior.
* Avoid using future rolling averages in training features.
* Keep source identifiers out of the model if they cause provider-specific leakage.
* Ensure duplicated station records do not appear in both training and test splits in a way that inflates performance.
* Validate separately across major cities when data volume supports it.
* Record all preprocessing versions with the model version.

## Retraining Strategy

| Trigger | Retraining Action |
| --- | --- |
| New historical dataset version | Rebuild training dataset and compare against current production model |
| Significant new live data volume | Add validated readings to training corpus after quality review |
| Model drift detected | Retrain and compare class-level metrics |
| Source schema changes | Revalidate preprocessing and retrain if feature distributions change |
| Poor Severe Risk recall | Investigate labels, class imbalance, thresholds, and model choice |
| ESG formula update | Recalculate related score metadata and validate interactions with risk outputs |

Recommended retraining cadence:

* Initial phase: manual retraining after each approved dataset expansion.
* Production phase: scheduled quarterly review, with emergency retraining if source drift or model degradation is detected.

Model versions must be stored with:

* Training dataset version.
* Feature schema version.
* Preprocessing version.
* Model artifact version.
* Evaluation report.
* Approval timestamp.

## Inference Pipeline

```text
Backend request
-> Resolve city or baseline climate_reading_id
-> Fetch latest validated reading or stored baseline
-> Validate required input fields
-> Normalize feature units
-> Build model feature vector
-> Load active model version
-> Generate risk category and probabilities
-> Calculate risk score and confidence
-> Calculate alert index
-> Calculate ESG and sustainability scores when requested
-> Store prediction record in Supabase
-> Return traceable response
```

If required real data is unavailable, inference must fail with a clear unavailable-data response rather than substituting fake values.

## Climate Impact Simulator Logic

The simulator is a scenario inference layer. It starts from a real baseline reading and replaces selected feature values with user-provided scenario inputs.

```text
Real baseline climate_reading
  AQI = observed value
  PM2.5 = observed value
  PM10 = observed value
  Temperature = observed value
  Humidity = observed value
  Rainfall = observed value
  Wind Speed = observed value
        |
        v
User scenario input
  Modified AQI, temperature, rainfall, humidity, PM2.5, PM10, or wind speed
        |
        v
Scenario feature vector
  Observed baseline values for unchanged fields
  User scenario values for modified fields
        |
        v
ML inference
  Simulated risk category
  Simulated risk score
  Confidence score
        |
        v
Comparison layer
  Baseline risk vs simulated risk
  Baseline ESG vs simulated ESG
  Baseline sustainability vs simulated sustainability
  Mitigation urgency
```

### Simulator Rules

1. A simulation must reference a real `baseline_climate_reading_id`.
2. User inputs must be validated for realistic ranges but remain labeled as scenario inputs.
3. Unchanged variables should come from the real baseline reading.
4. Changed variables should come from the user's scenario payload.
5. The same active model or a versioned simulator model should generate simulated risk outputs.
6. Results must store model version, baseline source, scenario inputs, and generated outputs.
7. Simulator outputs should never overwrite baseline observations.

### How Simulation Inputs Modify Prediction Outputs

Changing a scenario input changes the model feature vector. The new feature vector may shift:

* Risk category, for example Moderate Risk to High Risk.
* Risk score, for example a higher AQI increasing risk.
* Alert index, for example Yellow to Orange.
* ESG score delta, for example worsening air quality decreasing ESG score.
* Sustainability impact, for example increased pollution lowering sustainability score.
* Mitigation urgency, for example Severe Risk producing higher priority.

The simulator should always return both baseline and simulated context so users understand what changed and why.

## ESG Interaction With Predictions

ESG scoring is a calculated layer that uses real climate readings, pollution indicators, historical context, and prediction outputs.

```text
Validated climate reading
-> ML risk prediction
-> ESG scoring formula
-> Sustainability score
-> Alert index and recommendation context
```

### ESG Inputs

ESG and sustainability scoring may use:

* AQI
* PM2.5
* PM10
* Temperature
* Humidity
* Rainfall
* Wind speed
* Climate risk category
* Climate risk score
* Historical trend indicators

### ESG Output Interaction

| Prediction or Climate Signal | ESG Interaction |
| --- | --- |
| High AQI | Reduces ESG and sustainability score |
| High PM2.5 or PM10 | Reduces environmental quality component |
| Severe climate risk | Increases mitigation urgency and may reduce ESG score |
| Improving trend | Can improve sustainability interpretation if current values are acceptable |
| Worsening trend | Can reduce sustainability score and increase alert priority |
| Simulator risk increase | Produces ESG score delta and sustainability impact |

The ESG model should not be a hidden hardcoded score. It must use a documented formula version and source references. If ESG inputs are incomplete, the backend should return a partial or unavailable score status instead of inventing missing values.

## Model Outputs Stored In Supabase

| Output | Supabase Table | Required Metadata |
| --- | --- | --- |
| Climate risk category | `predictions` | `climate_reading_id`, model name, model version, predicted timestamp |
| Climate risk score | `predictions` | Input features, calculation metadata |
| Confidence score | `predictions` | Probability or calibration method |
| Alert index | `predictions` and `alert_history` | Threshold version and trigger metric |
| ESG score | `predictions` or future ESG table | Formula version and source inputs |
| Simulation output | `simulations` and optionally `predictions` | Baseline reading id, scenario inputs, model version |

## Monitoring Strategy

Production ML monitoring should track:

* Input feature distributions by city and source.
* Missing feature rates.
* External source freshness.
* Prediction class distribution.
* Severe Risk frequency.
* Confidence score distribution.
* Drift between historical training data and live inference data.
* User simulation volume and common scenario ranges.
* Prediction failures caused by unavailable source data.

Monitoring must not be converted into fake fallback predictions. If source data or model artifacts fail, the system should return explicit error or unavailable states.

## ML Readiness Checklist

Before implementation, confirm:

1. Exact dataset sources, licenses, formats, and download or ingestion methods.
2. Feature schema and unit standards.
3. Risk label generation or verified label source.
4. Missing value handling strategy per feature.
5. Train, validation, and test split strategy.
6. Baseline threshold model for comparison.
7. Random Forest hyperparameter search plan.
8. Evaluation metric acceptance criteria.
9. Model artifact storage and versioning plan.
10. Backend model loading and inference interface.
11. Simulator feature replacement rules.
12. ESG formula version and interaction rules.
13. Monitoring and retraining triggers.
14. Policy for unavailable source data during inference.
15. Confirmation that no notebooks, seed scripts, tests, or demo utilities introduce fake climate values.
