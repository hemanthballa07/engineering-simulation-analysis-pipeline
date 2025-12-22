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
