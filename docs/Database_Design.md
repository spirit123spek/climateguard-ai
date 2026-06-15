# Database Design

## users

Conceptual schema for registered platform users, authentication identity references, profile details, role or access level, organization context, and account timestamps.

## climate_readings

Conceptual schema for real environmental readings collected from approved live APIs and historical datasets, including source, location, timestamp, weather metrics, air quality metrics, and ingestion metadata.

## predictions

Conceptual schema for AI/ML climate risk predictions generated from real climate readings and historical datasets, including model metadata, risk category, confidence score, prediction horizon, and generated timestamp.

## simulations

Conceptual schema for AI Climate Impact Simulator runs, including user or organization reference, input assumptions based on real data, scenario parameters, computed impact metrics, recommendation summary, and simulation timestamp.

## reports

Conceptual schema for generated climate risk, ESG, simulation, and mitigation reports, including owner reference, report type, source data range, storage reference, generation status, and created timestamp.
