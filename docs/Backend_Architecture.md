# Backend Architecture

ClimateGuard AI uses a FastAPI backend as the trusted API, orchestration, validation, and integration layer between the frontend, external environmental data sources, the ML layer, and Supabase.

This document defines backend architecture and API contracts only. It does not create FastAPI code, route files, implementation files, or runtime configuration.

## Backend Principles

1. The frontend must not call OpenWeather, AQICN, Supabase service-role APIs, or ML internals directly.
2. The backend must never return fake, hardcoded, placeholder, or demo climate values.
3. Every metric returned by an API must be traceable to a live API, historical dataset, stored Supabase record, documented calculation, or ML model output.
4. User simulation inputs must be clearly marked as scenario inputs and never stored as observed climate readings.
5. Backend responses should include source metadata wherever climate, prediction, ESG, alert, simulation, or report data is displayed.
6. Backend writes to Supabase must respect the schema design and Row Level Security model.

## Backend Architecture Diagram

```text
Frontend
  React dashboard, simulator, reports, alerts
        |
        v
FastAPI Backend
  Auth middleware
  Request validation
  Service routing
  Rate limiting
  Structured logging
        |
        +--------------------+
        |                    |
        v                    v
External APIs           Supabase
  OpenWeather API         Supabase Auth
  AQICN API               Supabase PostgreSQL
  NASA EarthData          Supabase Storage
  Historical datasets
        |
        v
Processing Layer
  Source validation
  Unit normalization
  Missing-value handling
  Feature preparation
        |
        v
ML Layer
  Random Forest risk prediction
  Scenario inference
  Confidence metadata
        |
        v
Domain Engines
  ESG scoring
  Sustainability scoring
  Alert index
  Mitigation recommendations
  Report generation
        |
        v
Supabase Persistence
  climate_readings
  predictions
  simulations
  reports
  alert_history
  audit_logs
        |
        v
FastAPI Response
  Traceable JSON response or signed report download URL
```

## Backend Request Flow

```text
Frontend
-> FastAPI route
-> Authentication middleware
-> Request validation
-> Domain service
-> External APIs when live data is required
-> Processing and normalization layer
-> ML Layer when prediction or simulation is required
-> Supabase read or write
-> Audit log and structured application log
-> Response
```

For live climate requests, the backend should fetch OpenWeather and AQICN data, validate source timestamps and units, normalize values, store accepted readings in `climate_readings`, and return only validated values.

For prediction, ESG, alert, simulation, and report requests, the backend should use stored readings or freshly validated readings, then write outputs to the appropriate Supabase tables before responding when persistence is required.

## Backend Modules

| Service | Responsibility | Inputs | Outputs | Dependencies |
| --- | --- | --- | --- | --- |
| Auth Service | Validates Supabase JWTs, resolves application user profile, manages profile reads and updates, enforces ownership context | Supabase access token, profile payloads, request metadata | Authenticated user context, profile responses, auth errors | Supabase Auth, `users`, `audit_logs` |
| Climate Service | Fetches live OpenWeather and AQICN data, imports or reads historical data, validates and normalizes environmental readings | City, country, coordinates, source filters, date ranges | Validated readings, source metadata, freshness status, historical trends | OpenWeather API, AQICN API, historical datasets, `climate_readings`, `audit_logs` |
| Prediction Service | Prepares ML features, runs risk predictions, stores prediction records, returns risk category and confidence | Climate reading id, city, latest reading, optional simulation context | Risk category, risk score, confidence, model metadata, prediction id | Climate Service, ML Layer, `predictions`, `climate_readings`, `audit_logs` |
| ESG Service | Calculates ESG score, sustainability score, city sustainability score, and score changes from real data | Climate reading id, prediction id, city, date range, simulation result | ESG score, sustainability score, calculation metadata, score deltas | Climate Service, Prediction Service, `predictions`, `climate_readings`, `simulations` |
| Simulation Service | Runs AI Climate Impact Simulator scenarios using real baseline readings and user scenario inputs | User id, baseline reading id, city, scenario inputs | Simulation record, simulated risk, ESG delta, sustainability impact, mitigation urgency | Climate Service, Prediction Service, ESG Service, ML Layer, `simulations`, `predictions`, `audit_logs` |
| Alert Service | Creates and retrieves climate risk alerts based on risk score, alert index, source readings, and prediction outputs | User id, city, prediction id, reading id, alert thresholds | Alert records, active alert summary, acknowledgement status | Prediction Service, ESG Service, `alert_history`, `climate_readings`, `predictions`, `audit_logs` |
| Report Service | Generates traceable PDF report metadata and downloadable artifacts from stored readings, predictions, ESG scores, simulations, and alerts | User id, report type, city, date range, source references | Report metadata, status, Supabase Storage path, signed download URL | Supabase Storage, Climate Service, Prediction Service, ESG Service, Simulation Service, Alert Service, `reports`, `audit_logs` |

## Common API Conventions

Base path: `/api/v1`

Authentication:

* Protected endpoints require `Authorization: Bearer <supabase_access_token>`.
* Public endpoints should be limited to health or non-sensitive metadata only.
* Backend resolves the token to `users.auth_user_id` and then to `users.id`.

Common response metadata:

| Field | Purpose |
| --- | --- |
| `request_id` | Correlates frontend request, backend logs, and audit records |
| `data` | Successful response payload |
| `source_metadata` | Source names, timestamps, units, model versions, and calculation metadata when relevant |
| `errors` | Structured error list for failed requests |

Common error format:

| Field | Description |
| --- | --- |
| `code` | Stable machine-readable error code |
| `message` | Human-readable error summary |
| `details` | Optional structured details |
| `request_id` | Request correlation id |

Common error responses:

| HTTP Status | Error Code | Meaning |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | Request body or query parameters are invalid |
| 401 | `UNAUTHENTICATED` | Missing, expired, or invalid token |
| 403 | `FORBIDDEN` | Authenticated user cannot access the resource |
| 404 | `NOT_FOUND` | Requested record does not exist or is not visible to the user |
| 409 | `CONFLICT` | Request conflicts with current resource state |
| 422 | `SOURCE_DATA_UNAVAILABLE` | Required real source data is missing or unusable |
| 429 | `RATE_LIMITED` | Request exceeds rate limits |
| 502 | `EXTERNAL_SOURCE_ERROR` | External API or dataset provider failed |
| 503 | `MODEL_UNAVAILABLE` | ML layer or model artifact is unavailable |
| 500 | `INTERNAL_ERROR` | Unexpected backend failure |

## Authentication APIs

These endpoints define the backend contract. Supabase Auth may still handle credential verification internally, but the backend should own profile resolution, auditing, and application session context.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/auth/signup` | `{ "email": "string", "password": "string", "full_name": "string" }` | `{ "user": { "id": "uuid", "email": "string", "full_name": "string", "role": "user" }, "session": { "access_token": "string", "refresh_token": "string", "expires_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 409 `CONFLICT`, 500 `INTERNAL_ERROR` |
| POST | `/api/v1/auth/login` | `{ "email": "string", "password": "string" }` | `{ "user": { "id": "uuid", "email": "string", "role": "string" }, "session": { "access_token": "string", "refresh_token": "string", "expires_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 429 `RATE_LIMITED`, 500 `INTERNAL_ERROR` |
| POST | `/api/v1/auth/logout` | `{ "refresh_token": "string" }` | `{ "success": true }` | 401 `UNAUTHENTICATED`, 500 `INTERNAL_ERROR` |
| POST | `/api/v1/auth/refresh` | `{ "refresh_token": "string" }` | `{ "access_token": "string", "refresh_token": "string", "expires_at": "timestamp" }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 429 `RATE_LIMITED` |
| GET | `/api/v1/auth/me` | None | `{ "user": { "id": "uuid", "auth_user_id": "uuid", "email": "string", "full_name": "string", "role": "string", "preferences": {}, "default_city": "string" } }` | 401 `UNAUTHENTICATED`, 404 `NOT_FOUND` |
| PATCH | `/api/v1/auth/me` | `{ "full_name": "string", "default_city": "string", "default_country": "string", "preferences": {} }` | `{ "user": { "id": "uuid", "email": "string", "full_name": "string", "preferences": {}, "updated_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 403 `FORBIDDEN` |

## Climate APIs

Climate APIs return direct or imported environmental data. If source data is unavailable, the backend must return unavailable status rather than fabricated values.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/climate/current?city={city}&country={country}` | None | `{ "reading": { "id": "uuid", "city": "string", "temperature": "number|null", "humidity": "number|null", "rainfall": "number|null", "wind_speed": "number|null", "weather_condition": "string|null", "aqi": "number|null", "pm25": "number|null", "pm10": "number|null", "recorded_at": "timestamp", "ingested_at": "timestamp", "quality_status": "string" }, "source_metadata": { "weather_source": "OpenWeather API", "air_quality_source": "AQICN API", "units": {} } }` | 400 `VALIDATION_ERROR`, 422 `SOURCE_DATA_UNAVAILABLE`, 502 `EXTERNAL_SOURCE_ERROR`, 429 `RATE_LIMITED` |
| GET | `/api/v1/climate/readings/{reading_id}` | None | `{ "reading": { "id": "uuid", "source": "string", "source_type": "string", "city": "string", "metrics": {}, "recorded_at": "timestamp", "units": {}, "quality_status": "string" } }` | 401 `UNAUTHENTICATED`, 404 `NOT_FOUND` |
| GET | `/api/v1/climate/history?city={city}&metric={metric}&start_date={date}&end_date={date}` | None | `{ "city": "string", "metric": "string", "points": [ { "timestamp": "timestamp", "value": "number", "source": "string" } ], "source_metadata": { "sources": ["string"], "aggregation": "string" } }` | 400 `VALIDATION_ERROR`, 404 `NOT_FOUND`, 422 `SOURCE_DATA_UNAVAILABLE` |
| GET | `/api/v1/climate/trends?city={city}&start_date={date}&end_date={date}` | None | `{ "city": "string", "trends": { "temperature": [], "aqi": [], "pm25": [], "pm10": [], "rainfall": [] }, "source_metadata": { "sources": ["string"], "date_range": {} } }` | 400 `VALIDATION_ERROR`, 422 `SOURCE_DATA_UNAVAILABLE` |
| GET | `/api/v1/climate/sources/status?city={city}` | None | `{ "sources": [ { "name": "OpenWeather API", "status": "available|unavailable|degraded", "last_success_at": "timestamp" }, { "name": "AQICN API", "status": "available|unavailable|degraded", "last_success_at": "timestamp" } ] }` | 400 `VALIDATION_ERROR`, 502 `EXTERNAL_SOURCE_ERROR` |
| POST | `/api/v1/climate/ingest/historical` | `{ "source": "string", "dataset_ref": "string", "city": "string", "date_range": { "start": "date", "end": "date" } }` | `{ "ingestion_job": { "id": "string", "status": "queued|processing|completed|failed", "source": "string" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 409 `CONFLICT` |

## Prediction APIs

Prediction APIs must use trained models and real environmental inputs. They must store model version, input features, confidence where available, and source references.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/predictions` | `{ "city": "string", "climate_reading_id": "uuid|null" }` | `{ "prediction": { "id": "uuid", "climate_reading_id": "uuid", "risk_category": "Low Risk|Moderate Risk|High Risk|Severe Risk", "risk_score": "number", "confidence_score": "number|null", "alert_index": "Green|Yellow|Orange|Red", "model_name": "string", "model_version": "string", "predicted_at": "timestamp" }, "source_metadata": { "input_features": {}, "reading_source": "string" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 422 `SOURCE_DATA_UNAVAILABLE`, 503 `MODEL_UNAVAILABLE` |
| GET | `/api/v1/predictions/{prediction_id}` | None | `{ "prediction": { "id": "uuid", "risk_category": "string", "risk_score": "number", "confidence_score": "number|null", "esg_score": "number|null", "sustainability_score": "number|null", "alert_index": "string|null", "input_features": {}, "calculation_metadata": {} } }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND` |
| GET | `/api/v1/predictions?city={city}&limit={limit}` | None | `{ "predictions": [ { "id": "uuid", "city": "string", "risk_category": "string", "risk_score": "number", "predicted_at": "timestamp" } ] }` | 401 `UNAUTHENTICATED`, 400 `VALIDATION_ERROR` |
| GET | `/api/v1/predictions/latest?city={city}` | None | `{ "prediction": { "id": "uuid", "city": "string", "risk_category": "string", "risk_score": "number", "alert_index": "string", "predicted_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 404 `NOT_FOUND`, 422 `SOURCE_DATA_UNAVAILABLE` |

## ESG APIs

ESG APIs return calculated sustainability metrics derived from real environmental data, stored predictions, and documented formulas.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/esg/score` | `{ "city": "string", "climate_reading_id": "uuid|null", "prediction_id": "uuid|null" }` | `{ "esg": { "city": "string", "esg_score": "number", "sustainability_score": "number", "city_sustainability_score": "number", "calculated_at": "timestamp" }, "source_metadata": { "inputs": {}, "formula_version": "string" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 422 `SOURCE_DATA_UNAVAILABLE` |
| GET | `/api/v1/esg/city/{city}` | None | `{ "city": "string", "esg_score": "number", "sustainability_score": "number", "city_sustainability_score": "number", "source_metadata": {} }` | 400 `VALIDATION_ERROR`, 404 `NOT_FOUND`, 422 `SOURCE_DATA_UNAVAILABLE` |
| GET | `/api/v1/esg/history?city={city}&start_date={date}&end_date={date}` | None | `{ "city": "string", "points": [ { "timestamp": "timestamp", "esg_score": "number", "sustainability_score": "number", "source_prediction_id": "uuid" } ] }` | 400 `VALIDATION_ERROR`, 404 `NOT_FOUND` |
| GET | `/api/v1/esg/methodology` | None | `{ "methodology": { "formula_version": "string", "input_metrics": ["aqi", "pm25", "pm10", "temperature", "humidity", "rainfall", "wind_speed"], "data_policy": "real_data_only" } }` | 500 `INTERNAL_ERROR` |

## Simulation APIs

Simulation APIs accept user scenario inputs but must use a real baseline climate reading and trained prediction logic for outputs.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/simulations` | `{ "city": "string", "baseline_climate_reading_id": "uuid", "scenario_name": "string|null", "inputs": { "aqi": "number|null", "temperature": "number|null", "rainfall": "number|null", "humidity": "number|null", "wind_speed": "number|null", "pm25": "number|null", "pm10": "number|null" } }` | `{ "simulation": { "id": "uuid", "city": "string", "baseline_climate_reading_id": "uuid", "predicted_risk_category": "string", "predicted_risk_score": "number", "esg_score_delta": "number|null", "sustainability_impact": "number|null", "mitigation_urgency": "string|null", "created_at": "timestamp" }, "source_metadata": { "baseline_source": "string", "model_version": "string" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 422 `SOURCE_DATA_UNAVAILABLE`, 503 `MODEL_UNAVAILABLE` |
| GET | `/api/v1/simulations` | None | `{ "simulations": [ { "id": "uuid", "scenario_name": "string|null", "city": "string", "predicted_risk_category": "string|null", "created_at": "timestamp" } ] }` | 401 `UNAUTHENTICATED` |
| GET | `/api/v1/simulations/{simulation_id}` | None | `{ "simulation": { "id": "uuid", "scenario_inputs": {}, "baseline_climate_reading_id": "uuid", "predicted_risk_category": "string|null", "predicted_risk_score": "number|null", "risk_escalation": {}, "model_version": "string|null" } }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND` |
| PATCH | `/api/v1/simulations/{simulation_id}` | `{ "scenario_name": "string" }` | `{ "simulation": { "id": "uuid", "scenario_name": "string", "updated_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND` |
| DELETE | `/api/v1/simulations/{simulation_id}` | None | `{ "success": true }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND`, 409 `CONFLICT` |

## Alert APIs

Alert APIs expose generated alert history and active alert state based on real readings and prediction outputs.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/alerts/active?city={city}` | None | `{ "alerts": [ { "id": "uuid", "city": "string", "alert_index": "Green|Yellow|Orange|Red", "alert_level": "Safe|Moderate|High|Severe", "trigger_metric": "string", "trigger_value": "number|null", "message": "string", "created_at": "timestamp" } ] }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED` |
| GET | `/api/v1/alerts/history?city={city}&limit={limit}` | None | `{ "alerts": [ { "id": "uuid", "city": "string", "alert_index": "string", "delivery_status": "string", "created_at": "timestamp", "acknowledged_at": "timestamp|null" } ] }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED` |
| POST | `/api/v1/alerts/evaluate` | `{ "city": "string", "prediction_id": "uuid|null", "climate_reading_id": "uuid|null" }` | `{ "alert": { "id": "uuid", "alert_index": "string", "alert_level": "string", "trigger_metric": "string", "message": "string", "created_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 422 `SOURCE_DATA_UNAVAILABLE` |
| POST | `/api/v1/alerts/{alert_id}/acknowledge` | `{ "acknowledged": true }` | `{ "alert": { "id": "uuid", "delivery_status": "acknowledged", "acknowledged_at": "timestamp" } }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND` |

## Report APIs

Report APIs create metadata rows, generate report files using traceable stored data, and return private download access only to the report owner.

| Method | Route | Request Body | Response Body | Error Responses |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/reports` | `{ "report_type": "climate_risk|esg|simulation|historical_trend|combined", "city": "string|null", "date_range": { "start": "date|null", "end": "date|null" }, "simulation_id": "uuid|null" }` | `{ "report": { "id": "uuid", "status": "requested|processing", "report_type": "string", "city": "string|null", "created_at": "timestamp" } }` | 400 `VALIDATION_ERROR`, 401 `UNAUTHENTICATED`, 422 `SOURCE_DATA_UNAVAILABLE`, 409 `CONFLICT` |
| GET | `/api/v1/reports` | None | `{ "reports": [ { "id": "uuid", "report_type": "string", "city": "string|null", "status": "string", "generated_at": "timestamp|null", "created_at": "timestamp" } ] }` | 401 `UNAUTHENTICATED` |
| GET | `/api/v1/reports/{report_id}` | None | `{ "report": { "id": "uuid", "report_type": "string", "status": "string", "source_summary": {}, "storage_bucket": "string|null", "storage_path": "string|null", "generated_at": "timestamp|null" } }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND` |
| GET | `/api/v1/reports/{report_id}/download` | None | `{ "download": { "url": "string", "expires_at": "timestamp" } }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND`, 409 `CONFLICT` |
| DELETE | `/api/v1/reports/{report_id}` | None | `{ "success": true }` | 401 `UNAUTHENTICATED`, 403 `FORBIDDEN`, 404 `NOT_FOUND`, 409 `CONFLICT` |

## Authentication Flow

```text
Frontend obtains Supabase session
-> Frontend sends Supabase access token to FastAPI
-> FastAPI validates token with Supabase Auth/JWT verification
-> FastAPI resolves users.auth_user_id to users.id
-> FastAPI attaches user context to request
-> Domain service enforces ownership and role checks
-> Backend writes audit log for sensitive actions
-> Response returned to frontend
```

Signup and login may be implemented through Supabase Auth client flows or backend-mediated endpoints. Regardless of implementation choice, the backend must resolve an application `users` profile before allowing protected application operations.

## Authorization Strategy

| Resource | Authorization Rule |
| --- | --- |
| User profile | User can access only their own `users` row unless admin access is explicitly granted |
| Climate readings | Authenticated users can read validated shared readings; only backend service role can insert or update |
| Predictions | User can read own predictions; shared city predictions require controlled read policy |
| Simulations | User can access only simulations where `simulations.user_id` matches their profile |
| Reports | User can access only reports where `reports.user_id` matches their profile |
| Report downloads | Backend must verify report ownership before issuing signed URL |
| Alerts | User can access user-specific alerts assigned to them; shared city alerts require controlled read policy |
| Audit logs | Restricted to service role and authorized admins |
| Historical ingestion | Admin or trusted backend job only |

## Rate Limiting Considerations

| Area | Suggested Limit Strategy |
| --- | --- |
| Auth endpoints | Strict per-IP and per-email limits to reduce brute-force attempts |
| Live climate fetch | Per-user and per-city limits to protect OpenWeather and AQICN quotas |
| Prediction endpoints | Per-user limits because ML inference consumes backend resources |
| Simulation endpoints | Per-user limits, with stricter limits for repeated scenario runs |
| Report generation | Queue-based limit per user and per time window because PDF generation and storage have cost |
| Historical ingestion | Admin-only and job-level throttling |
| Download URLs | Short-lived signed URLs and per-user download throttling |

When rate limited, the backend should return 429 `RATE_LIMITED` with a retry window. Rate limits must never trigger fallback fake data.

## Logging Strategy

Backend logging should combine structured application logs and persistent audit logs.

Application logs:

* Include `request_id`, route, method, status code, latency, user id when authenticated, city when relevant, and external source status.
* Do not log API secrets, access tokens, refresh tokens, passwords, or full raw source payloads unless explicitly configured for secure debugging.
* Log source failures with provider name and request context.
* Log model inference errors with model name and version, not sensitive internals.

Audit logs:

* Write to `audit_logs` for profile changes, simulation creation, report generation, climate ingestion jobs, prediction generation jobs, alert creation, report downloads, admin actions, and security-sensitive failures.
* Use `actor_type` for system, ingestion job, ML job, user, or admin actions.
* Preserve `entity_type`, `entity_id`, city context, and structured metadata.

## External Dependency Failure Policy

| Dependency | Failure Behavior |
| --- | --- |
| OpenWeather API | Return unavailable source status or stale stored reading only if clearly labeled with timestamp |
| AQICN API | Return unavailable source status or stale stored reading only if clearly labeled with timestamp |
| Historical dataset source | Mark ingestion job failed or partial; do not fabricate missing trend points |
| ML Layer | Return `MODEL_UNAVAILABLE`; do not return dummy prediction outputs |
| Supabase PostgreSQL | Return persistence or retrieval error; do not serve untraceable generated values |
| Supabase Storage | Keep report status failed or processing until storage succeeds |

## API Contract Readiness Checklist

Before implementing FastAPI routes, confirm:

1. Exact request and response schemas using Pydantic models.
2. Supabase Auth verification approach for backend requests.
3. Role names and admin authorization rules.
4. External API key storage and secret management.
5. OpenWeather and AQICN response normalization rules.
6. Historical dataset ingestion workflow and supported source formats.
7. ML model artifact loading and version metadata format.
8. ESG scoring formula version and allowed score ranges.
9. Alert threshold definitions for Green, Yellow, Orange, and Red.
10. Report generation queue or synchronous generation strategy.
11. Rate limiting backend or middleware choice.
12. Structured logging fields and audit log event vocabulary.
13. Error code vocabulary and frontend error handling expectations.
14. No endpoint should seed, return, or persist fake climate values.
