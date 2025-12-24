.PHONY: setup test sweep analyze visualize pipeline ci-local clean all api ui insights smoke

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

# Run Design Optimization (Calibration)
optimize:
	.venv/bin/python scripts/calibrate.py

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

# --- Day 5: API & UI ---
api:
	.venv/bin/uvicorn api.app:app --reload --port 8000

ui:
	.venv/bin/streamlit run ui/dashboard.py

insights:
	.venv/bin/python scripts/generate_ai_insights.py --batch-dir results/runs

# --- CI ---
test-api:
	.venv/bin/pytest tests/test_api.py

smoke:
	@echo "Running Local Smoke Test..."
	# 1. Fast Sweep
	SWEEP_CONFIG=configs/sweep_ci.yaml OUTPUT_ROOT=results/runs_smoke .venv/bin/python simulations/sweep.py
	# 2. Ingest
	.venv/bin/python scripts/ingest_data.py --runs-dir results/runs_smoke
	# 3. Mock AI
	.venv/bin/python scripts/generate_ai_insights.py --batch-dir results/runs_smoke --mock
	@echo "Smoke Test Complete. Check results/runs_smoke/"
