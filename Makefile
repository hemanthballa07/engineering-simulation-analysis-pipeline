.PHONY: setup test sweep analyze visualize pipeline ci-local clean all

# Setup proper environment
setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

# Run Unit & Integration Tests
test:
	.venv/bin/pytest tests/

# Run the parameter sweep simulation (Standard)
sweep:
	.venv/bin/python simulations/sweep.py

# Run the analysis script to aggregate results
analyze:
	.venv/bin/python scripts/analyze.py

# Generate plotting artifacts
visualize:
	.venv/bin/python scripts/visualize.py

# Run the full pipeline (Standard Sweep)
pipeline: test sweep analyze visualize
	@echo "Standard Pipeline completed successfully."

# Run the CI pipeline locally (Fast Sweep)
ci-local:
	@echo "Running Local CI Simulation..."
	.venv/bin/pytest -q tests/
	SWEEP_CONFIG=configs/sweep_ci.yaml OUTPUT_ROOT=results/runs_ci .venv/bin/python simulations/sweep.py
	RESULTS_ROOT=results/runs_ci .venv/bin/python scripts/analyze.py
	RESULTS_ROOT=results/runs_ci .venv/bin/python scripts/visualize.py
	@echo "Local CI Pipeline completed. Check results/runs_ci and artifacts/."

# Clean up results and artifacts
clean:
	rm -rf results/* artifacts/*

# Helper to run everything from scratch
all: clean pipeline
