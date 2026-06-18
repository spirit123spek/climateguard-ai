# Data Source Mapping

ClimateGuard AI must display only metrics that can be traced to a real source, dataset, trained model, or documented calculation. This document defines the first architecture-level contract for where each displayed value comes from, how it is collected, how it is processed, where it is stored, and how often it should be refreshed.

## Architecture Review Summary

The platform should separate raw data ingestion from user-facing analytics. Live API values are collected by backend services, validated, normalized, and stored before they are used by dashboards, machine learning predictions, ESG scoring, simulations, recommendations, or reports.

Historical datasets should be imported through controlled ingestion jobs and tagged with source metadata, date ranges, geographic coverage, and quality checks. Machine learning outputs and calculated metrics should never be created without linked input records. Supabase should act as the system of record for users, readings, predictions, simulations, reports, source metadata, and generated artifacts.

## Markdown Architecture Diagram

```text
External APIs and Datasets
  OpenWeather API
  AQICN API
  NASA EarthData
  India Open Government Data
  Historical Climate Datasets
        |
        v
Backend Services
  API client services
  Dataset ingestion services
  Authentication-aware request handlers
  Report generation services
        |
        v
Processing Layer
  Source validation
  Unit normalization
  Location normalization
  Timestamp normalization
  Missing-value handling
  Data quality checks
        |
        v
ML Layer
  Feature preparation
  Random Forest risk prediction
  Scenario prediction
  Model confidence tracking
        |
        v
Supabase
  Supabase Auth
  Supabase PostgreSQL
  Supabase Storage
        |
        v
Frontend
  Monitoring dashboard
  Historical analytics
  ESG and sustainability views
  Climate impact simulator
  Risk alerts
  Mitigation recommendations
  PDF report downloads
```

## Source Ownership

| Source | Primary Responsibility | Data Type | Collection Method | Storage Target |
| --- | --- | --- | --- | --- |
| OpenWeather API | Live weather and atmospheric conditions | Directly fetched | Backend API client requests by selected city or coordinates | `climate_readings` |
| AQICN API | Live AQI and pollutant readings | Directly fetched | Backend API client requests by selected city or station | `climate_readings` |
| NASA EarthData | Historical and satellite-supported environmental datasets | Directly imported dataset records | Scheduled or manual dataset ingestion pipeline | `climate_readings` or future historical dataset tables |
| India Open Government Data | India-specific historical environmental and climate datasets | Directly imported dataset records | Scheduled or manual dataset ingestion pipeline | `climate_readings` or future historical dataset tables |
| Historical Climate Datasets | Historical weather, air quality, and climate records for training and trend analysis | Directly imported dataset records | Dataset ingestion pipeline with source metadata | `climate_readings` or future historical dataset tables |
| Supabase Auth | User identity and authentication state | User generated | Supabase Auth signup, login, and session management | `users` linked to Supabase Auth identity |
| Supabase PostgreSQL | Application system of record | Stored source, calculated, predicted, and user-generated records | Backend write operations after validation | `users`, `climate_readings`, `predictions`, `simulations`, `reports` |
| Supabase Storage | Generated report artifacts and exported files | Generated artifact storage | Backend report generation upload | Report file paths referenced by `reports` |

## A. Live API Data

| Displayed Data Point | Source | Collection Method | Storage Location | Processing Logic | Update Frequency | Value Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected city current temperature | OpenWeather API | Backend fetch by city or coordinates | `climate_readings.temperature` | Validate timestamp and location, normalize unit to Celsius unless user settings require another unit | On dashboard refresh and scheduled city refresh | Directly fetched |
| Selected city humidity | OpenWeather API | Backend fetch by city or coordinates | `climate_readings.humidity` | Validate percentage range and source timestamp | On dashboard refresh and scheduled city refresh | Directly fetched |
| Selected city rainfall or precipitation | OpenWeather API | Backend fetch by city or coordinates | `climate_readings.rainfall` | Normalize precipitation amount and time window, store missing rainfall as unavailable rather than zero unless source confirms zero | On dashboard refresh and scheduled city refresh | Directly fetched |
| Selected city wind speed | OpenWeather API | Backend fetch by city or coordinates | `climate_readings.wind_speed` | Normalize unit, validate non-negative values | On dashboard refresh and scheduled city refresh | Directly fetched |
| Atmospheric condition | OpenWeather API | Backend fetch by city or coordinates | `climate_readings.weather_condition` | Preserve source condition label and optional normalized category | On dashboard refresh and scheduled city refresh | Directly fetched |
| AQI | AQICN API | Backend fetch by city, station, or coordinates | `climate_readings.aqi` | Validate scale metadata, store source station and timestamp | On dashboard refresh and scheduled city refresh | Directly fetched |
| PM2.5 | AQICN API | Backend fetch by city, station, or coordinates | `climate_readings.pm25` | Validate pollutant unit and source timestamp | On dashboard refresh and scheduled city refresh | Directly fetched |
| PM10 | AQICN API | Backend fetch by city, station, or coordinates | `climate_readings.pm10` | Validate pollutant unit and source timestamp | On dashboard refresh and scheduled city refresh | Directly fetched |
| Pollution metrics | AQICN API | Backend fetch by city, station, or coordinates | `climate_readings.pollution_metrics` | Store available pollutant values with source names, units, and timestamps | On dashboard refresh and scheduled city refresh | Directly fetched |
| Reading timestamp | OpenWeather API and AQICN API | Captured from source response and backend ingestion time | `climate_readings.recorded_at`, `climate_readings.ingested_at` | Keep both source observation time and platform ingestion time | Every successful ingestion | Directly fetched and system recorded |
| Data source name | OpenWeather API and AQICN API | Captured during backend collection | `climate_readings.source` | Store source identifier for traceability | Every successful ingestion | Directly fetched and system recorded |

## B. Historical Dataset Data

| Displayed Data Point | Source | Collection Method | Storage Location | Processing Logic | Update Frequency | Value Type |
| --- | --- | --- | --- | --- | --- | --- |
| Historical temperature trend | NASA EarthData, India Open Government Data, Historical Climate Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Normalize location, date, and temperature units; aggregate by day, month, or selected period | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Historical rainfall trend | NASA EarthData, India Open Government Data, Historical Climate Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Normalize precipitation units and time windows; aggregate by selected period | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Historical AQI trend | India Open Government Data, Historical Air Quality Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Normalize AQI scale metadata and station or location mapping | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Historical PM2.5 trend | India Open Government Data, Historical Air Quality Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Normalize units, source timestamps, and station metadata | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Historical PM10 trend | India Open Government Data, Historical Air Quality Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Normalize units, source timestamps, and station metadata | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Pollution trend | India Open Government Data, Historical Air Quality Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Aggregate available pollutant indicators by location and period | Dataset refresh schedule, initially manual or periodic | Directly imported and calculated for trend display |
| Environmental change indicators | NASA EarthData and Historical Climate Datasets | Dataset ingestion pipeline | `climate_readings` or future historical dataset tables | Compare current or recent values against historical baselines | Dataset refresh schedule and analytics recalculation | Calculated from imported data |
| ML training features | NASA EarthData, India Open Government Data, Historical Climate Datasets, stored live readings | Dataset ingestion and backend feature extraction | Future model training datasets or derived feature storage | Validate labels, remove invalid records, preserve feature provenance | Per model training cycle | Directly imported and processed |

## C. ML Generated Data

| Displayed Data Point | Source | Collection Method | Storage Location | Processing Logic | Update Frequency | Value Type |
| --- | --- | --- | --- | --- | --- | --- |
| Climate risk category | Random Forest Classifier trained on real environmental data | Backend ML inference using latest validated readings | `predictions.risk_category` | Predict Low Risk, Moderate Risk, High Risk, or Severe Risk from AQI, PM2.5, PM10, temperature, humidity, rainfall, and wind speed | After new validated readings or user simulation input | Predicted |
| Climate risk score | ML prediction engine | Backend ML inference and score normalization | `predictions.risk_score` | Convert model probability or calibrated risk output into a documented numeric score | After new validated readings or user simulation input | Predicted |
| Prediction confidence | ML prediction engine | Backend ML inference metadata | `predictions.confidence_score` | Store model confidence or calibrated probability with model version | Every prediction | Predicted |
| Risk escalation estimate | ML prediction engine with historical trend features | Backend ML inference using current readings and trend context | `predictions.escalation_estimate` | Estimate likely movement in risk level over the selected prediction horizon | After prediction refresh or trend recalculation | Predicted |
| Future climate risk from simulator | ML prediction engine | Backend simulation inference using user scenario inputs and real baseline readings | `simulations.predicted_risk_category` | Replace selected variables with user scenario values while preserving real baseline context | Per simulation run | Predicted |
| Simulated risk score | ML prediction engine | Backend simulation inference | `simulations.predicted_risk_score` | Generate risk score from scenario features and model version | Per simulation run | Predicted |
| Mitigation urgency | ML prediction engine and recommendation rules | Backend evaluation using predicted risk, ESG impact, and alert index | `simulations.mitigation_urgency` or future recommendation records | Map predicted severity and sustainability impact to urgency level | Per prediction or simulation run | Predicted and calculated |

## D. Calculated Metrics

| Displayed Data Point | Source | Collection Method | Storage Location | Processing Logic | Update Frequency | Value Type |
| --- | --- | --- | --- | --- | --- | --- |
| ESG Score | OpenWeather API, AQICN API, historical datasets, ML outputs | Backend calculation from validated stored readings and prediction records | `predictions.esg_score` or future ESG records | Weighted sustainability calculation based on air quality, pollution, environmental quality, climate conditions, and documented weights | After new validated readings, prediction refresh, or simulation run | Calculated |
| Sustainability Score | OpenWeather API, AQICN API, historical datasets | Backend calculation from validated current and historical indicators | `predictions.sustainability_score` or future sustainability records | Normalize environmental indicators to a 0-100 scale using documented formulas and real source data | After new validated readings or trend recalculation | Calculated |
| Personalized city sustainability score | OpenWeather API, AQICN API, historical datasets | Backend calculation by selected city | `predictions.city_sustainability_score` or future city score records | Combine current air quality, pollution, temperature, and historical indicators for a selected city | After new city readings or historical refresh | Calculated |
| Climate Risk Alert Index | Climate risk score, climate risk category, and escalation estimate | Backend calculation from prediction outputs | `predictions.alert_index` | Map risk and escalation into Green, Yellow, Orange, or Red with documented thresholds | After prediction refresh | Calculated |
| ESG score change from simulator | Baseline ESG score and simulated scenario values | Backend simulation calculation | `simulations.esg_score_delta` | Compare baseline ESG score against scenario ESG score | Per simulation run | Calculated |
| Sustainability impact from simulator | Baseline sustainability score and simulated scenario values | Backend simulation calculation | `simulations.sustainability_impact` | Compare baseline and scenario sustainability scores with documented scoring logic | Per simulation run | Calculated |
| Risk escalation from simulator | Baseline prediction and simulated prediction | Backend simulation calculation | `simulations.risk_escalation` | Compare baseline and simulated risk categories or scores | Per simulation run | Calculated |
| Mitigation recommendation list | Predictions, ESG score, alert index, and simulator results | Backend recommendation engine | Future recommendation records or embedded report metadata | Rank actions by expected environmental impact and urgency using documented rules | After prediction or simulation refresh | Calculated |
| Mitigation priority ranking | Predictions, ESG score, alert index, and simulator results | Backend recommendation engine | Future recommendation records or embedded report metadata | Sort mitigation actions into high, medium, or low priority based on documented thresholds | After prediction or simulation refresh | Calculated |
| Report summary metrics | Stored readings, predictions, simulations, and calculated metrics | Backend report generation service | `reports` metadata and Supabase Storage artifact | Compile only traceable stored metrics and source references into generated report | Per report generation request | Calculated |

## E. User Generated Data

| Displayed Data Point | Source | Collection Method | Storage Location | Processing Logic | Update Frequency | Value Type |
| --- | --- | --- | --- | --- | --- | --- |
| User profile | Supabase Auth and user input | Signup, login, and profile update flows | `users` | Link platform profile to Supabase Auth identity | On account creation or profile update | User generated |
| Selected city | User input | Frontend city selection submitted to backend | Request context and optional user preferences in `users` | Validate city name or coordinates before fetching source data | Per user search or preference update | User generated |
| Simulation AQI input | User input with real baseline context | Climate Impact Simulator scenario form | `simulations.input_aqi` | Validate range and mark as scenario input, not observed data | Per simulation run | User generated |
| Simulation temperature input | User input with real baseline context | Climate Impact Simulator scenario form | `simulations.input_temperature` | Validate unit and mark as scenario input, not observed data | Per simulation run | User generated |
| Simulation rainfall input | User input with real baseline context | Climate Impact Simulator scenario form | `simulations.input_rainfall` | Validate unit and time window, mark as scenario input | Per simulation run | User generated |
| Simulation humidity input | User input with real baseline context | Climate Impact Simulator scenario form | `simulations.input_humidity` | Validate percentage range, mark as scenario input | Per simulation run | User generated |
| Simulation scenario metadata | User input and system metadata | Climate Impact Simulator run submission | `simulations` | Store scenario name, selected city, baseline reading references, model version, and created timestamp | Per simulation run | User generated and system recorded |
| Report generation request | User action | Report export flow | `reports` | Store requested report type, selected date range, city, generation status, and storage path | Per report request | User generated and system recorded |

## Value Classification

| Classification | Definition | Examples |
| --- | --- | --- |
| Directly fetched | Returned by an approved live API or imported from a real historical dataset without being invented by the application | AQI, PM2.5, PM10, temperature, humidity, rainfall, wind speed |
| Calculated | Derived from direct source data, stored predictions, user scenario inputs, or documented formulas | ESG Score, Sustainability Score, Alert Index, trend averages, score deltas, recommendation rankings |
| Predicted | Produced by a trained ML model using real input features and versioned model logic | Climate risk category, climate risk score, prediction confidence, simulated future risk |
| User generated | Entered or triggered by a user and clearly labeled as user input or request metadata | Selected city, simulation variable inputs, report request, user profile |

## Storage Mapping

| Storage Location | Data Stored | Notes |
| --- | --- | --- |
| `users` | User profile, Supabase Auth identity reference, preferences, selected default city if needed | No climate metrics should be invented or cached here without source references |
| `climate_readings` | Live and historical environmental readings, source name, source timestamp, ingestion timestamp, location metadata | Stores direct observations and imported dataset records |
| `predictions` | ML risk outputs, confidence, ESG score, sustainability score, alert index, model version, input reading references | Every prediction must link to real input readings or validated simulation context |
| `simulations` | User scenario inputs, baseline reading references, simulated predictions, score changes, mitigation urgency | Scenario inputs must be clearly separated from observed environmental readings |
| `reports` | Report metadata, owner, report type, source data range, generation status, Supabase Storage path | Reports must only compile traceable stored data |
| Supabase Storage | Generated PDF reports and other exported artifacts | File metadata should point back to `reports` |

## Real Data Integrity Policy

* No fake climate values.
* No hardcoded ESG scores.
* No demo analytics.
* No dummy prediction outputs.
* No manually invented AQI, temperature, rainfall, humidity, wind speed, PM2.5, or PM10 values.
* Every displayed metric must have a documented source.
* Every calculated metric must have documented input records and calculation logic.
* Every predicted metric must store the model version, input features, prediction timestamp, and confidence where available.
* User simulation inputs must be labeled as scenario inputs and must never be stored as observed climate readings.
* If a source API or dataset does not provide a required value, the application must display the value as unavailable instead of substituting fake or static data.
* Reports must include only traceable real-data metrics, calculated metrics, or model outputs derived from real data.

## Implementation Principles For Future Development

1. Backend services must fetch external data; the frontend should not directly call climate APIs with exposed secrets.
2. All external source responses should be validated before storage or display.
3. Stored records should preserve source name, source timestamp, ingestion timestamp, city or coordinates, and units.
4. Processing logic should normalize units before ML inference, ESG scoring, sustainability scoring, alerts, and reports.
5. Dashboards should read from validated backend responses or stored Supabase records, not hardcoded constants.
6. Historical analytics should use imported datasets or stored readings, never fabricated trend series.
7. ML predictions should be reproducible from stored input references and model version metadata.
8. Simulation outputs should clearly distinguish observed baseline values from user-modified scenario values.
