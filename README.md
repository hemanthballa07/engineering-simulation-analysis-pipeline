# Engineering Simulation & Analysis Pipeline

![Build Status](https://github.com/hemanthballa07/engineering-simulation-analysis-pipeline/actions/workflows/pipeline.yaml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

## Overview

This repository implements a professional-grade simulation pipeline for the 1D Heat Equation. It demonstrates end-to-end engineering practices including numerical solvers, reproducible parameter sweeps, data aggregation, automated visualization, and Continuous Integration (CI).

**Key Capabilities:**
- **Simulation**: Explicit Finite Difference solver with stability enforcement.
- **Experimentation**: YAML-driven parameter sweeps for design space exploration.
- **Analysis**: Aggregation of metrics (convergence, energy, stability) into summary reports.
- **Visualization**: Automated generation of temperature profiles and sensitivity plots.
- **CI/CD**: GitHub Actions pipeline validating the entire flow on every commit.

## Directory Structure

```text
├── configs/          # Simulation configurations (base and sweep)
├── simulations/      # Source code for solver and sweep logic
├── analysis/         # Metrics computation and aggregation scripts
├── visualization/    # Plotting logic
├── tests/            # Pytest test suite
├── scripts/          # Orchestration scripts (analyze, visualize)
├── results/          # Local simulation outputs (gitignored)
├── artifacts/        # Generated reports and plots (gitignored)
├── Makefile          # Developer convenience commands
└── .github/          # CI pipeline configuration
```

## Local Usage

### Prerequisites
- Python 3.9+

### 1. Setup
Create a virtual environment and install dependencies:
```bash
make setup
```

### 2. Run Pipeline
Execute the full workflow (Tests -> Sweep -> Analyze -> Visualize):
```bash
make pipeline
```

### 3. Individual Steps
You can run individual stages of the pipeline:

**Run a Parameter Sweep:**
```bash
make sweep
# Output: results/runs/
```

**Run Design Optimization:**
```bash
make optimize
# Output: Finds 'alpha' for a target temperature.
```

**Analyze Results:**
```bash
make analyze
# Output: artifacts/summary.csv, artifacts/summary.md
```

**Generate Visualizations:**
```bash
make visualize
# Output: artifacts/temp_profiles.png, artifacts/metric_sweep.png
```

## Continuous Integration

The repository is configured with GitHub Actions (`.github/workflows/pipeline.yaml`). On every `push` and `pull_request`, the system:
1.  Sets up the environment.
2.  Runs the test suite (`pytest`).
3.  Executes a fast "CI-specific" parameter sweep (`configs/sweep_ci.yaml`).
4.  Aggregates metrics and generates plots.
5.  Uploads the resulting artifacts for review.

## Outputs

After running the pipeline, the following artifacts are generated in the `artifacts/` directory:

-   `summary.csv`: Comprehensive metrics for all simulation runs.
-   `summary.md`: Markdown summary table of results.
-   `top_runs.md`: Ranking of runs based on energy minimization.
-   `temp_profiles.png`: Overlay plot of final temperature profiles.
-   `metric_sweep.png`: Scatter plot showing parameter sensitivity.

## 🏗️ Architecture (Platform Extension)
The pipeline has been extended into a cloud-native platform:

1.  **Simulation Engine**: Python-based verified numerical solver.
2.  **Metrics Layer**: Semantic abstraction normalizing raw data into decision-ready metrics.
3.  **Analytics Store**: SQL-based storage for large-scale aggregation.
4.  **Cloud Storage**: Azure Blob Storage for artifact persistence.

## 📊 Metrics Layer & Decision Readiness
We use a **canonical metrics contract** (`metrics/metrics_schema.json`) to decouple the simulation engine from downstream consumers.
-   **Performance Metrics**: `max_temperature`, `stability_ratio`.
-   **Quality Metrics**: `converged`, `steps`.
-   **Validation**: Every run is validated against physics constraints (e.g., $T_{max} \ge T_{min}$) before ingestion.

## 🧠 AI-Assisted Insights (Azure OpenAI)
The platform uses LLMs to act as a "Senior Principal Engineer", analyzing the validated metrics to generate actionable reports.

### Configuration
Set the following environment variables:
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
# Or fallback to standard OpenAI
export OPENAI_API_KEY="sk-..."
```

### Generation
To generate insights for a batch of runs:
```bash
make insights
```
This generates `{run_id}.insights.json` and `{run_id}.insights.md` in the `insights/` folder.

## 🖥️ API & Visualization (FastAPI + Streamlit)
We provide a dedicated dashboard for exploring runs and AI insights.

### 1. Start the API (Backend)
The API serves validated artifacts and metrics.
```bash
make api
# Running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 2. Start the Dashboard (Frontend)
The UI connects to the local API to visualize results.
```bash
make ui
# Opens in browser at http://localhost:8501
```
