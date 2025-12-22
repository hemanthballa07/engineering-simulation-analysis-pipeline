# Engineering Simulation & Analysis Pipeline

A Python-based simulation and analysis pipeline for running parameter sweeps, comparing engineering design variants, and producing reproducible evaluation artifacts with CI/CD automation.

## Project Structure

- `simulations/`: Core physics solvers and sweep runners.
- `analysis/`: Scripts to aggregate results and compute metrics.
- `visualization/`: Plotting scripts for artifacts.
- `configs/`: YAML configuration files for runs and sweeps.
- `scripts/`: Helper scripts for local execution.
- `tests/`: Unit and integration tests.
- `.github/workflows/`: CI/CD automation.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run a single simulation (Coming in Step 1).

3. Run the tests:
   ```bash
   pytest tests/
   ```

## Methodology

Uses a finite difference method for the 1D heat equation diffusion problem.
`dT/dt = alpha * d2T/dx2`
