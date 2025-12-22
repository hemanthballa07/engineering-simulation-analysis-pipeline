.PHONY: setup test sweep analyze visualize pipeline clean all

# Setup proper environment
setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

# Run Unit & Integration Tests
test:
	.venv/bin/pytest tests/

# Run the parameter sweep simulation
sweep:
	.venv/bin/python simulations/sweep.py

# Run the analysis script to aggregate results
analyze:
	.venv/bin/python analysis/compare_runs.py

# Generate plotting artifacts
visualize:
	.venv/bin/python visualization/plot_simulations.py

# Run the full pipeline (Local CI simulation)
pipeline: test sweep analyze visualize
	@echo "Pipeline completed successfully."

# Clean up results and artifacts
clean:
	rm -rf results/* artifacts/*

# Helper to run everything from scratch
all: clean pipeline
