.PHONY: setup test sweep analyze visualize pipeline ci-local clean all

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest tests/

sweep:
	.venv/bin/python simulations/sweep.py

analyze:
	.venv/bin/python scripts/analyze.py

visualize:
	.venv/bin/python scripts/visualize.py

pipeline: test sweep analyze visualize

# CI-like sweep for local validation
ci-local:
	.venv/bin/pytest -q tests/
	SWEEP_CONFIG=configs/sweep_ci.yaml OUTPUT_ROOT=results/runs_ci .venv/bin/python simulations/sweep.py
	RESULTS_ROOT=results/runs_ci .venv/bin/python scripts/analyze.py
	RESULTS_ROOT=results/runs_ci .venv/bin/python scripts/visualize.py

clean:
	rm -rf results/* artifacts/*

all: clean pipeline
