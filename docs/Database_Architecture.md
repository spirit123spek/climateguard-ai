# Database Architecture

ClimateGuard AI uses Supabase PostgreSQL as the system of record for authenticated users, real environmental readings, historical dataset imports, prediction outputs, ESG and sustainability metrics, simulator runs, alert history, reports, and audit events.

This document is a design artifact only. It does not define SQL, migrations, or actual Supabase tables.

## Design Principles

1. Every displayed metric must be traceable to a live API, historical dataset, model output, documented calculation, or user action.
2. User simulation inputs must be stored separately from observed climate readings.
3. Prediction and scoring records must reference their input readings, model version, and calculation context.
4. Reports must reference stored source records and generated artifacts in Supabase Storage.
5. Audit logs must capture security-sensitive and data-changing actions.
6. Row Level Security should isolate user-owned records while allowing controlled access to shared public environmental readings.

## Entity Summary

| Entity | Purpose | Stores |
| --- | --- | --- |
| `users` | Application profile linked to Supabase Auth | User identity metadata, preferences, role |
| `climate_readings` | Real live and historical environmental observations | Weather, AQI, pollutants, source metadata |
| `predictions` | ML outputs and calculated risk or sustainability scores | Risk category, risk score, ESG score, alert index |
| `simulations` | User-driven climate scenario runs | Scenario inputs, baseline references, simulated outputs |
| `reports` | Generated report metadata and storage references | Report type, status, source range, file path |
| `alert_history` | Climate alert events shown or sent to users | Alert level, trigger metric, delivery status |
| `audit_logs` | Security, data, and system activity trace | Actor, action, entity, timestamp, metadata |

## Entity Relationship Diagram

```text
Supabase Auth
    |
    | 1:1
    v
users
    |
    | 1:N
    +--------------------+
    |                    |
    v                    v
simulations          reports
    |                    ^
    | N:1                |
    v                    |
climate_readings --------+
    |
    | 1:N
    v
predictions
    |
    | 1:N
    v
alert_history

users
    |
    | 1:N
    v
audit_logs

reports may reference predictions, simulations, and climate_readings through metadata or explicit foreign keys.
audit_logs may reference any entity through entity_type and entity_id metadata.
```

## users

### Purpose

Stores application-level profile data for authenticated users. Authentication itself is handled by Supabase Auth; this table extends that identity with ClimateGuard-specific profile and preference metadata.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the application user profile |
| `auth_user_id` | UUID | Supabase Auth user identifier |
| `full_name` | Text | User display name |
| `email` | Text | User email copied from Supabase Auth for application display and lookup |
| `role` | Text | User access role such as user, analyst, or admin |
| `default_city` | Text | Optional preferred city for dashboard loading |
| `default_country` | Text | Optional preferred country |
| `preferences` | JSON | User settings such as units, notification settings, and report preferences |
| `created_at` | Timestamp | Profile creation timestamp |
| `updated_at` | Timestamp | Last profile update timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique application user profile |
| Foreign Key | `auth_user_id` | References Supabase Auth user identity |

Relationships:

* One user can create many simulations.
* One user can generate many reports.
* One user can receive many alert history records.
* One user can produce many audit log records as the actor.

## climate_readings

### Purpose

Stores real environmental readings collected from live APIs and imported historical datasets. This is the foundational data source for dashboards, trend analysis, ML predictions, ESG scoring, alert generation, simulations, and reports.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the climate reading |
| `source` | Text | Source name such as OpenWeather API, AQICN API, NASA EarthData, India Open Government Data, or Historical Climate Dataset |
| `source_type` | Text | Live API or historical dataset |
| `source_record_id` | Text | Optional source-provided station, dataset, or record identifier |
| `city` | Text | City associated with the reading |
| `country` | Text | Country associated with the reading |
| `latitude` | Decimal | Reading latitude when available |
| `longitude` | Decimal | Reading longitude when available |
| `recorded_at` | Timestamp | Source observation timestamp |
| `ingested_at` | Timestamp | Platform ingestion timestamp |
| `temperature` | Decimal | Temperature normalized to the platform unit standard |
| `humidity` | Decimal | Humidity percentage |
| `rainfall` | Decimal | Rainfall or precipitation amount using documented units |
| `wind_speed` | Decimal | Wind speed using documented units |
| `weather_condition` | Text | Source weather condition label or normalized condition |
| `aqi` | Decimal | Air Quality Index from approved source |
| `pm25` | Decimal | PM2.5 pollutant value |
| `pm10` | Decimal | PM10 pollutant value |
| `pollution_metrics` | JSON | Additional pollutant metrics with source units and names |
| `units` | JSON | Unit metadata for stored values |
| `quality_status` | Text | Validation status such as valid, partial, rejected, or needs_review |
| `raw_source_payload_ref` | Text | Optional storage reference for raw source payload if retained |
| `created_at` | Timestamp | Row creation timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique reading record |

Relationships:

* One climate reading can be used by many predictions.
* One climate reading can be used as the baseline for many simulations.
* One climate reading can be included in many reports through report metadata or report source references.
* Climate readings do not require direct user ownership because the same city reading can support many users.

## predictions

### Purpose

Stores ML prediction outputs and related calculated metrics derived from validated real climate readings or validated simulation context. This includes climate risk category, climate risk score, ESG score, sustainability score, alert index, model metadata, and calculation provenance.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the prediction |
| `climate_reading_id` | UUID | Reading used as the prediction baseline |
| `user_id` | UUID | Optional user who requested or viewed the prediction |
| `simulation_id` | UUID | Optional simulation that generated the prediction |
| `model_name` | Text | ML model name such as Random Forest Classifier |
| `model_version` | Text | Version of the model used |
| `input_features` | JSON | Feature values used for inference |
| `risk_category` | Text | Low Risk, Moderate Risk, High Risk, or Severe Risk |
| `risk_score` | Decimal | Numeric climate risk score |
| `confidence_score` | Decimal | Model confidence or calibrated probability |
| `esg_score` | Decimal | Calculated ESG score derived from real data and documented logic |
| `sustainability_score` | Decimal | Calculated sustainability score |
| `city_sustainability_score` | Decimal | City-level sustainability score when applicable |
| `alert_index` | Text | Green, Yellow, Orange, or Red alert classification |
| `escalation_estimate` | JSON | Predicted risk movement or escalation metadata |
| `calculation_metadata` | JSON | Formula version, thresholds, and source references for calculated values |
| `predicted_at` | Timestamp | Prediction generation timestamp |
| `created_at` | Timestamp | Row creation timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique prediction record |
| Foreign Key | `climate_reading_id` | References `climate_readings.id` |
| Foreign Key | `user_id` | References `users.id` when prediction is user-requested |
| Foreign Key | `simulation_id` | References `simulations.id` when prediction belongs to a scenario run |

Relationships:

* One prediction belongs to one baseline climate reading.
* One prediction may belong to one user.
* One prediction may belong to one simulation.
* One prediction can create many alert history records.
* Reports can include many prediction records through report metadata or source references.

## simulations

### Purpose

Stores Climate Impact Simulator scenario runs. Simulation inputs are user-generated scenario values and must never be treated as observed climate readings. Each simulation should reference a real baseline reading and store predicted or calculated scenario results.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the simulation |
| `user_id` | UUID | User who created the simulation |
| `baseline_climate_reading_id` | UUID | Real reading used as the scenario baseline |
| `scenario_name` | Text | Optional user-defined scenario name |
| `city` | Text | City for the scenario |
| `input_aqi` | Decimal | User scenario AQI |
| `input_temperature` | Decimal | User scenario temperature |
| `input_rainfall` | Decimal | User scenario rainfall |
| `input_humidity` | Decimal | User scenario humidity |
| `input_wind_speed` | Decimal | Optional user scenario wind speed |
| `input_pm25` | Decimal | Optional user scenario PM2.5 |
| `input_pm10` | Decimal | Optional user scenario PM10 |
| `scenario_inputs` | JSON | Full scenario input payload and units |
| `predicted_risk_category` | Text | ML-predicted future risk category |
| `predicted_risk_score` | Decimal | ML-predicted scenario risk score |
| `esg_score_delta` | Decimal | Change from baseline ESG score |
| `sustainability_impact` | Decimal | Change from baseline sustainability score |
| `risk_escalation` | JSON | Scenario risk escalation details |
| `mitigation_urgency` | Text | Urgency level derived from scenario outcome |
| `model_name` | Text | ML model used for simulation inference |
| `model_version` | Text | Model version used |
| `created_at` | Timestamp | Simulation creation timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique simulation record |
| Foreign Key | `user_id` | References `users.id` |
| Foreign Key | `baseline_climate_reading_id` | References `climate_readings.id` |

Relationships:

* One user can create many simulations.
* One simulation uses one real baseline climate reading.
* One simulation can produce one or more predictions.
* One simulation can be included in many reports.
* One simulation can produce audit log entries.

## reports

### Purpose

Stores metadata for generated climate risk, ESG, simulation, and mitigation reports. Generated PDF files should be stored in Supabase Storage, while this table stores traceability, status, ownership, and file references.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the report |
| `user_id` | UUID | User who requested the report |
| `report_type` | Text | Climate risk, ESG, simulation, historical trend, or combined report |
| `city` | Text | City covered by the report |
| `date_range_start` | Date | Beginning of included data range |
| `date_range_end` | Date | End of included data range |
| `source_summary` | JSON | Referenced readings, predictions, simulations, and source metadata |
| `status` | Text | Requested, processing, completed, failed, or expired |
| `storage_bucket` | Text | Supabase Storage bucket name |
| `storage_path` | Text | Supabase Storage file path |
| `generated_at` | Timestamp | Successful generation timestamp |
| `expires_at` | Timestamp | Optional report expiration timestamp |
| `created_at` | Timestamp | Request creation timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique report record |
| Foreign Key | `user_id` | References `users.id` |

Relationships:

* One user can generate many reports.
* A report can summarize many climate readings, predictions, and simulations through `source_summary`.
* Report files are stored in Supabase Storage and referenced by bucket and path.

## alert_history

### Purpose

Stores generated climate risk alerts and alert delivery history. This preserves what alert was shown or sent, why it was triggered, and which prediction or reading caused it.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the alert record |
| `user_id` | UUID | User who received or viewed the alert, if user-specific |
| `climate_reading_id` | UUID | Reading that contributed to the alert |
| `prediction_id` | UUID | Prediction that triggered the alert |
| `city` | Text | Alert city |
| `alert_index` | Text | Green, Yellow, Orange, or Red |
| `alert_level` | Text | Safe, Moderate, High, or Severe |
| `trigger_metric` | Text | Metric that triggered the alert, such as AQI, risk_score, or PM2.5 |
| `trigger_value` | Decimal | Trigger value when applicable |
| `message` | Text | Human-readable alert message |
| `delivery_channel` | Text | Dashboard, email, notification, or report |
| `delivery_status` | Text | Created, shown, sent, failed, or acknowledged |
| `created_at` | Timestamp | Alert creation timestamp |
| `acknowledged_at` | Timestamp | Optional user acknowledgement timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique alert record |
| Foreign Key | `user_id` | References `users.id` when user-specific |
| Foreign Key | `climate_reading_id` | References `climate_readings.id` |
| Foreign Key | `prediction_id` | References `predictions.id` |

Relationships:

* One prediction can create many alert records.
* One climate reading can contribute to many alert records.
* One user can receive many alert records.

## audit_logs

### Purpose

Stores immutable security, data access, and data mutation events. Audit logs help verify user isolation, report generation, simulation creation, data ingestion operations, administrative actions, and failure investigations.

### Fields

| Field | Data Type | Description |
| --- | --- | --- |
| `id` | UUID | Primary key for the audit event |
| `actor_user_id` | UUID | User who performed the action, if applicable |
| `actor_type` | Text | User, system, admin, ingestion_job, or ml_job |
| `action` | Text | Action name such as create_simulation, generate_report, ingest_reading, or update_profile |
| `entity_type` | Text | Entity affected by the action |
| `entity_id` | UUID | Identifier of affected entity when available |
| `city` | Text | Optional city context for climate-related operations |
| `ip_address` | Text | Request IP address when available |
| `user_agent` | Text | Request user agent when available |
| `metadata` | JSON | Additional structured audit context |
| `created_at` | Timestamp | Audit event timestamp |

### Keys And Relationships

| Key Type | Field | Relationship |
| --- | --- | --- |
| Primary Key | `id` | Unique audit event |
| Foreign Key | `actor_user_id` | References `users.id` when action is user-driven |

Relationships:

* One user can have many audit log records.
* Audit logs can reference any entity using `entity_type` and `entity_id`.
* System jobs can create audit records without a user foreign key.

## Data Category Storage Map

| Data Category | Primary Tables | Notes |
| --- | --- | --- |
| Live API Data | `climate_readings` | OpenWeather API and AQICN API readings with source metadata and timestamps |
| Historical Data | `climate_readings` initially, future specialized historical tables if volume requires | NASA EarthData, India Open Government Data, historical climate and air quality datasets |
| Prediction Results | `predictions` | ML risk category, risk score, confidence, model metadata, input feature provenance |
| ESG Scores | `predictions` initially, future ESG-specific table if scoring becomes complex | ESG score, sustainability score, city sustainability score, calculation metadata |
| Simulation Results | `simulations`, `predictions` | User scenario inputs in `simulations`, scenario ML outputs may also be represented in `predictions` |
| User Activity | `users`, `reports`, `simulations`, `alert_history`, `audit_logs` | Profile, report requests, simulator actions, alert interactions, security and mutation history |

## Data Retention Strategy

### Live Climate Data Retention

Live API readings should be retained long enough to support dashboards, short-term trend analysis, prediction reproducibility, and report generation. A practical starting policy is to keep high-resolution live readings for 12 to 24 months, then aggregate older readings into daily or monthly summaries if storage volume becomes significant.

Raw source payload references, if stored, should have shorter retention than normalized readings unless needed for audit or model reproducibility.

### Historical Dataset Retention

Historical dataset records should be retained as long-term analytical assets because they support model training, trend analysis, baselines, forecasting, and sustainability calculations. Each historical import should preserve source metadata, import timestamp, and dataset version or date range.

### Prediction History Retention

Prediction records should be retained for traceability, model evaluation, alert review, and report reproducibility. Predictions linked to generated reports should not be deleted while the report remains available. Older prediction records may be archived after a defined retention period if model audit requirements are satisfied.

### Simulation Retention

User simulations should be retained as user-owned history so users can compare scenarios over time. Users may be allowed to delete their simulations, subject to audit and report linkage rules. Simulations referenced by generated reports should remain available while the report is retained.

### Alert History Retention

Alert history should be retained for operational visibility, user notification history, and climate risk review. A practical starting policy is to keep alert history for at least 12 months, with longer retention for severe alerts and alerts included in reports.

### Report Storage Policy

Generated PDF reports should be stored in Supabase Storage with metadata in `reports`. Reports may have an expiration timestamp if storage cost controls are required. Metadata should be retained longer than files so the platform can show that a report existed, who requested it, and which sources were used.

### Audit Log Retention

Audit logs should be append-only and retained according to security, compliance, and operational requirements. A practical starting policy is to retain audit logs for at least 24 months, with restricted access and no user-facing editing capability.

## Indexing Strategy

Indexes should support the most common dashboard, report, simulation, and audit queries without over-indexing early.

| Entity | Candidate Indexes | Reason |
| --- | --- | --- |
| `users` | `auth_user_id`, `email`, `role` | Authentication lookup, account lookup, admin filtering |
| `climate_readings` | `city`, `country`, `recorded_at`, `ingested_at`, `source`, `source_type`, `latitude` plus `longitude` | City dashboard queries, time-series charts, source filtering, geospatial lookups |
| `predictions` | `climate_reading_id`, `user_id`, `simulation_id`, `predicted_at`, `risk_category`, `alert_index`, `city` if stored or derived | Latest prediction lookup, user history, alert filtering, reports |
| `simulations` | `user_id`, `baseline_climate_reading_id`, `city`, `created_at`, `predicted_risk_category` | User simulation history, city scenario queries, high-risk scenario filtering |
| `reports` | `user_id`, `report_type`, `city`, `status`, `created_at`, `generated_at` | User report lists, report generation queue, report history |
| `alert_history` | `user_id`, `prediction_id`, `climate_reading_id`, `city`, `alert_index`, `created_at`, `delivery_status` | User alerts, city alert history, severe alert filtering, delivery status checks |
| `audit_logs` | `actor_user_id`, `actor_type`, `action`, `entity_type`, `entity_id`, `created_at` | Security review, incident investigation, user activity tracing |

Composite index candidates:

* `climate_readings(city, recorded_at)` for city time-series dashboards.
* `climate_readings(source, recorded_at)` for source-specific data quality checks.
* `predictions(user_id, predicted_at)` for user prediction history.
* `simulations(user_id, created_at)` for simulator history.
* `reports(user_id, created_at)` for report lists.
* `alert_history(user_id, created_at)` for user alert timelines.
* `audit_logs(entity_type, entity_id)` for entity-level audit review.

## Security Considerations

### Row Level Security

Supabase Row Level Security should be enabled for user-owned tables. Users should only read and modify their own profile, simulations, reports, user-specific alerts, and user-visible audit events if any audit data is exposed.

Shared environmental readings may be readable by authenticated users through controlled policies, but inserts and updates should be restricted to backend service roles or ingestion jobs.

### User Isolation

User-owned records should include `user_id` and enforce policies based on the authenticated Supabase user. Reports, simulations, alert acknowledgement, and profile preferences must not be visible across accounts unless an explicit team or organization model is introduced later.

### Service Role Boundaries

External API ingestion, dataset imports, prediction creation, report generation, and audit log writes should be performed by trusted backend services using secure server-side credentials. The frontend should not receive OpenWeather, AQICN, Supabase service role, or dataset ingestion secrets.

### Audit Logging

Security-sensitive and data-changing events should create audit log records. This includes login-relevant profile changes, simulation creation, report generation, climate data ingestion jobs, prediction generation jobs, alert creation, and administrative changes.

### Data Integrity

Foreign keys should preserve traceability from predictions to readings, simulations to baseline readings, reports to users, and alerts to predictions. Calculated and predicted records should store model versions, calculation metadata, and source references.

### Sensitive Data

Personal user data should be minimized. Report files and audit logs may contain sensitive user activity and should use restrictive access policies. Raw source payloads should be retained only if needed and protected from public access.

## Supabase Implementation Readiness

| Entity | Supabase PostgreSQL Mapping | RLS Readiness | Storage Integration |
| --- | --- | --- | --- |
| `users` | Maps to a profile table linked to Supabase Auth using `auth_user_id` | User can read and update own profile; admins can manage according to role policy | No direct file storage |
| `climate_readings` | Maps to a readings table for live API and historical dataset observations | Authenticated users may read approved records; writes restricted to backend service role | Optional raw payload references if retained |
| `predictions` | Maps to a prediction results table linked to readings, users, and optionally simulations | Users can read their own user-requested predictions; shared city predictions require controlled read policy | No direct file storage |
| `simulations` | Maps to a user-owned simulator history table | Users can create, read, update labels for, and delete their own simulation records subject to retention rules | No direct file storage |
| `reports` | Maps to report metadata table linked to user ownership and Supabase Storage paths | Users can access only their own reports; report generation writes restricted to backend | Stores bucket and path for generated PDFs |
| `alert_history` | Maps to alert event table linked to predictions, readings, and users when user-specific | Users can read and acknowledge their own alerts; system creates alert records | No direct file storage |
| `audit_logs` | Maps to append-only audit event table | General users should not directly access audit logs; admins and service roles may access restricted records | No direct file storage |

Implementation notes for future migrations:

1. Use UUID primary keys for all application tables.
2. Use timestamp fields consistently for creation, source observation, ingestion, prediction, and report generation events.
3. Use JSON fields only for flexible metadata, source payload summaries, calculation metadata, and model feature snapshots.
4. Prefer explicit scalar columns for frequently filtered metrics such as city, timestamp, AQI, temperature, risk category, and alert index.
5. Keep observed readings, user scenario inputs, calculated values, and predicted outputs clearly separated.
6. Do not create tables until schema details, RLS policies, and ingestion workflows are reviewed together.
