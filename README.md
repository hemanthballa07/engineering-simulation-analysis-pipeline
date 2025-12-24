# Engineering Simulation & Analysis Pipeline

## What this is
**Engineering Simulation & Analysis Platform (Cloud + SQL + AI + Observability)**
A cloud-native analytics platform that runs parameter sweeps, persists artifacts to a data lake, loads results into SQL for analytics, generates validated decision metrics, and produces auditable AI summaries (prompt-logged + schema-validated). Includes a read-only API and Streamlit dashboard for exploring runs and comparisons, with correlation-ID structured logging and CI smoke tests.

**Key capabilities**
- **Cloud ecosystem**: Artifact persistence (Azure Blob) with safe no-op when creds absent
- **Data Engineering**: SQL analytics layer + verified queries for aggregation and variant comparison
- **Governance**: Validated metrics contract + physics sanity checks + golden dataset
- **Decision Intelligence**: AI insights generation (audit logs + strict JSON schema validation)
- **User Interface**: Read-only API + dashboard to explore runs/metrics/insights/compare
- **Operations**: Structured logging + correlation IDs + CI pipeline smoke test (offline)

![Build Status](https://github.com/hemanthballa07/engineering-simulation-analysis-pipeline/actions/workflows/pipeline.yaml/badge.svg)

## 🏗️ Architecture

```text
Simulation Sweep → Artifacts → Azure Blob (optional)
                → ETL → SQL DB → Analytics Queries
                → Metrics Extraction + Validation
                → AI Insights (prompt logged + schema validated)
                → FastAPI → Streamlit Dashboard
                → Observability + CI smoke artifacts
```

## Directory Structure

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


## 🖥️ Dashboard & Decision Platform (Soft UI)
A professional-grade **Streamlit Dashboard** (`make ui`) provides a "Decision Platform" experience:

- **Soft UI Design**: Modern "Cloud/Blue" aesthetic with 20px rounded cards, deep navy sidebar, and gradient hero indicators.
- **Decision Engine**: Automatically computes "Decision Summaries" (e.g., *"Candidate is Safer and +15% Stable"*) in Comparison Mode.
- **Metdata Dense**: Every view renders critical context (Grid Size, Time Step, Runtime) to build trust.
- **Actionable AI**: Displays AI-generated executive summaries and allows on-demand insight generation.

### 1. Start the API (Backend)
The API serves validated artifacts and metrics, resiliently finding runs across local, smoke, or CI directories.
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

### 3. Generate Insights (Deterministically)
To hydrate the dashboard with engineering assessments (functioning even without API keys via mock mode):
```bash
make insights
```

## 🛠️ Developer Tools & Cleanup
- **Smoke Test**: `make smoke` (Runs full pipeline + API + UI check in isolation).
- **Cleanup**: `make clean` (Removes generated artifacts).
