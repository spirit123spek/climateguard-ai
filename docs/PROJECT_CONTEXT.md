# PROJECT CONTEXT FOR CODEX

You are assisting in building a real-world software project called:

# ClimateGuard AI

### Real-Time AI-Based Climate Risk Assessment and Mitigation Platform Using Artificial Intelligence

---

# PROJECT VISION

ClimateGuard AI is NOT a college demo project.

It is being designed as a real-world, production-oriented climate intelligence platform that can be used by actual users.

The platform must use real environmental data, real APIs, real datasets, and real machine learning predictions.

No fake data, mock analytics, hardcoded climate values, placeholder predictions, or demo-only functionality should exist in the final product.

Every dashboard, chart, metric, prediction, score, recommendation, and report must originate from authentic data sources.

---

# PROBLEM STATEMENT

Most climate and weather applications only display current environmental conditions such as temperature and AQI.

They do not help users understand:

* Climate risk
* Future environmental impact
* Sustainability implications
* ESG impact
* Mitigation priorities

ClimateGuard AI aims to solve this by combining:

* Real-time environmental monitoring
* Machine Learning risk prediction
* ESG sustainability analysis
* Climate impact simulation
* Decision-support recommendations

into a single platform.

---

# MAIN OBJECTIVES

1. Monitor real-time environmental conditions.
2. Predict climate-related risks using AI.
3. Generate ESG sustainability scores.
4. Analyze historical environmental trends.
5. Simulate future climate scenarios.
6. Recommend mitigation actions.
7. Generate downloadable reports.
8. Support sustainability-focused decision making.

---

# CORE FEATURES

## Real-Time Climate Monitoring

Users select a city.

The platform fetches live:

* Temperature
* Humidity
* Rainfall
* Wind Speed
* AQI
* PM2.5
* PM10
* Pollution Metrics

using real APIs.

No manually entered climate data should be displayed.

---

## Climate Risk Prediction

The platform uses Machine Learning to predict:

* Low Risk
* Moderate Risk
* High Risk
* Severe Risk

based on environmental conditions.

The prediction system must use trained models and real environmental data.

---

## ESG Sustainability Scoring

Generate sustainability metrics based on:

* Air quality
* Pollution
* Environmental quality
* Climate conditions

The ESG score must be data-driven.

---

## Historical Climate Analytics

Analyze:

* AQI trends
* Temperature trends
* Pollution trends
* Environmental changes

using historical datasets.

---

## Mitigation Recommendation Engine

Generate intelligent recommendations based on:

* Current conditions
* Predicted risk
* Sustainability impact

Examples:

* Reduce emissions
* Increase urban greenery
* Promote public transportation
* Improve water conservation

---

# SIGNATURE FEATURE

## AI Climate Impact Simulator

This is the project's most important innovation.

Users can modify climate variables such as:

* AQI
* Temperature
* Rainfall
* Humidity

The system then predicts:

* Future climate risk
* ESG score changes
* Sustainability impact
* Risk escalation
* Mitigation urgency

Example:

Current AQI = 180

User simulates AQI = 250

System predicts:

* Severe Risk
* ESG score decrease
* Increased health impact
* Higher mitigation priority

This transforms the platform from a monitoring system into a climate decision-support system.

---

# ADDITIONAL FEATURES

## Personalized City Sustainability Score

Generate sustainability ratings for cities.

Based on:

* AQI
* Pollution
* Temperature
* Environmental indicators

Example:

Delhi = 42/100

Mumbai = 63/100

Noida = 55/100

---

## Climate Risk Alert Index

Generate:

* Green (Safe)
* Yellow (Moderate)
* Orange (High)
* Red (Severe)

Also estimate how quickly risk may escalate.

---

## AI Mitigation Priority Ranking

Rank actions by expected environmental impact.

Example:

Public Transport Improvement = High Impact

Tree Plantation = Medium Impact

Water Conservation = Low Impact

---

# REAL DATA POLICY

This is mandatory.

The project must use:

## Live APIs

OpenWeather API

Used for:

* Temperature
* Humidity
* Rainfall
* Wind Speed
* Atmospheric Conditions

AQICN API

Used for:

* AQI
* PM2.5
* PM10
* Air Quality Metrics

---

## Historical Datasets

NASA EarthData

India Open Government Data

Climate Datasets

Air Quality Datasets

Historical Weather Datasets

These datasets are used for:

* Model training
* Trend analysis
* Forecasting
* Sustainability calculations

---

# MACHINE LEARNING

Initial model:

Random Forest Classifier

Inputs:

* AQI
* PM2.5
* PM10
* Temperature
* Humidity
* Rainfall
* Wind Speed

Outputs:

* Low Risk
* Moderate Risk
* High Risk
* Severe Risk

The system must be designed so additional models can be integrated later.

---

# TECHNOLOGY STACK

Frontend:

* React.js
* Tailwind CSS
* Recharts

Backend:

* FastAPI

Database:

* Supabase PostgreSQL

Authentication:

* Supabase Auth

Storage:

* Supabase Storage

Machine Learning:

* Python
* Scikit-learn

Deployment:

* Vercel
* Render

Version Control:

* GitHub

Development Environment:

* VS Code

AI Assistance:

* Codex

UI Design:

* Figma

---

# SYSTEM ARCHITECTURE

Live APIs + Historical Datasets
↓
Data Collection Layer
↓
Data Validation Layer
↓
Data Processing Layer
↓
Machine Learning Layer
↓
Climate Risk Assessment Engine
↓
ESG Sustainability Engine
↓
AI Climate Impact Simulator
↓
Mitigation Recommendation Engine
↓
Report Generation Engine
↓
Dashboard & Analytics Layer
↓
Supabase Database
↓
User Interface

---

# DEVELOPMENT PRINCIPLES

1. Build production-quality code.
2. Use modular architecture.
3. Follow clean code practices.
4. Design for scalability.
5. Use TypeScript where appropriate.
6. Avoid hardcoded values.
7. Avoid fake analytics.
8. Avoid mock climate data.
9. Prefer reusable components.
10. Ensure mobile responsiveness.
11. Ensure accessibility.
12. Document architecture decisions.

---

# WHAT NOT TO DO

Do NOT:

* Generate fake climate values.
* Use placeholder ESG scores.
* Hardcode dashboard analytics.
* Create demo-only functionality.
* Use dummy prediction outputs.
* Build features that are disconnected from real data.

Every metric displayed must be traceable to a real source, dataset, model, or calculation.

---

# ROLE OF CODEX

Act as the lead software architect and engineering assistant for ClimateGuard AI.

When generating code, architecture, database design, APIs, or project structure:

* Follow the project vision.
* Preserve real-data requirements.
* Maintain clean architecture.
* Design for future scalability.
* Prioritize production-ready implementation over shortcuts.

Always assume this project will be used by real users and not merely demonstrated in a classroom.
