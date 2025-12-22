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
├── simulations/      # Core solver logic and sweep runner
├── analysis/         # Scripts to aggregate results into summary tables
├── visualization/    # Plotting scripts for artifacts
├── tests/            # Unit and integration tests (pytest)
├── scripts/          # Helper scripts (pipeline runner)
├── results/          # (Generated) Raw output: metadata.json, timeseries.csv, metrics.json
├── artifacts/        # (Generated) Final reports and plots (PNG, CSV, MD)
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
This runs: **Tests** -> **Sweep** -> **Analysis** -> **Visualization**.

### 3. View Results
Check the `artifacts/` folder:
- `summary.md`: A summary table of all runs and their metrics.
- `temp_profiles.png`: Comparision of temperature profiles.
- `metric_sweep.png`: Parameter sensitivity plot.

## ⚙️ Configuration

### `configs/base.yaml`
Defines the default physical parameters:
```yaml
simulation:
  L: 1.0
  nx: 50
  alpha: 0.1
  t_max: 0.5
```

### `configs/sweep.yaml`
Defines parameters to vary:
```yaml
sweep:
  alpha: [0.01, 0.1, 1.0]
  nx: [20, 50]
```

## 📊 Method

### Physics
We solve the 1D transient heat conduction equation with Dirichlet boundary conditions ($T(0)=0, T(L)=0$) and an initial Gaussian peak.
$$ \frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} $$

### Solver
- **Method**: Explicit Finite Difference (FTCS).
- **Stability**: Automated check guarantees $r = \frac{\alpha \Delta t}{\Delta x^2} \le 0.5$.

## 🤖 CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/pipeline.yaml`) that triggers on push:
1.  Installs dependencies.
2.  Runs Unit Tests (`pytest`).
3.  Executes the Parameter Sweep.
4.  Generates Analysis & Plots.
5.  Uploads `results/` and `artifacts/` as build artifacts.

## 📋 Artifact Examples

### Temperature Profiles
*(Generated image placed in artifacts/temp_profiles.png)*
<img src="artifacts/temp_profiles.png" width="600" alt="Temperature Profiles">

### Parameter Sweep Analysis
*(Generated image placed in artifacts/metric_sweep.png)*
<img src="artifacts/metric_sweep.png" width="600" alt="Metric Sweep">

---
*Created by Antigravity*
