# Interview Preparation Guide

## 1. Resume Bullets (FD&E aligned)
*   Built a cloud-native engineering analytics platform: parameter sweeps → artifact persistence → SQL analytics → validated metrics → auditable AI summaries, exposed via read-only API and dashboard.
*   Implemented governance and reliability: metrics contract + physics sanity validation, strict JSON-schema enforcement for AI outputs, and prompt/audit logging for traceability.
*   Added production-grade operations: correlation-ID structured logging across pipeline and services, plus CI smoke tests that generate and publish reproducible artifacts offline.

## 2. LinkedIn Project Description
**Title**: Cloud-Native Engineering Analytics Platform (Azure + SQL + AI Insights)

**Description**:
Built an end-to-end analytics platform for running parameter sweeps and converting raw simulation outputs into decision-ready insights. The system persists artifacts to Azure Blob (optional), loads results into a SQL analytics store, extracts validated metrics (schema + physics checks), and generates auditable AI summaries with prompt logging and strict JSON-schema validation. Includes a read-only FastAPI service and Streamlit dashboard for exploring runs and comparisons, plus correlation-ID structured logging and CI smoke tests for reproducibility.

## 3. The "90-Second Story" (Memorize)
"I built a cloud-native analytics platform around my simulation pipeline. Runs produce artifacts that can be uploaded to Azure Blob and ingested into a SQL store for analytics queries like aggregation and variant comparison. 

I added a validated metrics contract with physics sanity checks and golden runs, so downstream consumers never see invalid data. 

On top of that, I generate AI insights using a strict schema and prompt logging for auditability—no fabricated numbers, everything cites metrics. 

Finally, I exposed it through a read-only API and Streamlit dashboard, and added correlation-ID structured logging plus a CI smoke pipeline that reproduces artifacts offline. The result is an end-to-end data + AI experience that’s operable, testable, and decision-focused."
