# Engineering Simulation & Analysis Pipeline

A Python-based simulation and analysis pipeline for running parameter sweeps, comparing engineering design variants (Heat Equation), and producing reproducible evaluation artifacts with CI/CD automation.

![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-green)

## 🚀 Overview

This repository demonstrates a professional engineering software workflow:
1.  **Simulation**: Solves the 1D Heat Equation (`dT/dt = alpha * d2T/dx2`) using a finite difference method.
2.  **Experimentation**: Runs automated parameter sweeps (cartesian product of configuration).
3.  **Analysis**: Aggregates metrics (energy, max temp, convergence) into summary reports.
4.  **Visualization**: Automatically generates temperature profiles and parameter sensitivity plots.
5.  **Automation**: Full CI/CD pipeline via GitHub Actions.

## 📂 Directory Structure

```text
├── configs/          # YAML configuration files (base parameters + sweep ranges)
├── simulations/      # Core solver logic + sweep runner
├── analysis/         # Metrics library and aggregation logic
├── visualization/    # Plotting scripts
├── tests/            # Pytest suite (Unit + Integration)
├── scripts/          # Pipeline runner scripts (analyze.py, visualize.py)
├── results/          # Generated output (metadata.json, metrics.json, timeseries.csv)
├── artifacts/        # Generated reports and plots (PNG, CSV, MD)
└── .github/          # CI/CD workflow configuration
```

## 🛠️ Quick Start

### 1. Setup Environment
```bash
# Using Make (Recommended)
make setup

# Or manual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
```bash
make pipeline
```
This runs: **Tests** → **Sweep** → **Analysis** → **Visualization**.

### 3. Run Fast CI Simulation Locally
To test the CI workflow locally (using a smaller parameter set):
```bash
make ci-local
```

## ⚙️ Configuration

- **Results**: Stored in `results/runs/` by default.
- **Config**:
    - `configs/base.yaml`: Default physical parameters ($L=1.0, nx=50, \alpha=0.1$).
    - `configs/sweep.yaml`: Production parameter sweep ranges.
    - `configs/sweep_ci.yaml`: Fast sweep ranges for CI.

## 📊 Method

### Physics
We solve the 1D transient heat conduction equation with Dirichlet boundary conditions ($T(0)=0, T(L)=0$) and an initial Gaussian peak.
$$ \frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} $$

### Solver
- **Method**: Explicit Finite Difference (FTCS).
- **Stability**: Automated check guarantees $r = \frac{\alpha \Delta t}{\Delta x^2} \le 0.5$.

## 🤖 CI/CD Automation

The project includes a GitHub Actions workflow (`.github/workflows/pipeline.yaml`) that triggers on push:
1.  **Tests**: Runs `pytest`.
2.  **CI Sweep**: Runs `simulations/sweep.py` with `configs/sweep_ci.yaml`.
3.  **Analysis**: Aggregates results from compliance runs.
4.  **Artifacts**: Uploads plots and summary tables to GitHub Actions Artifacts.

## 📋 Artifact Examples

### Temperature Profiles
*(Generated image placed in artifacts/temp_profiles.png)*
<img src="artifacts/temp_profiles.png" width="600" alt="Temperature Profiles">

### Parameter Sweep Analysis
*(Generated image placed in artifacts/metric_sweep.png)*
<img src="artifacts/metric_sweep.png" width="600" alt="Metric Sweep">

---
*Created by Antigravity*
