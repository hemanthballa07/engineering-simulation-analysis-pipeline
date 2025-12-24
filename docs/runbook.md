# Operational Runbook

## 1. Observability & Logging
All components emit structured JSON logs. Use `jq` to parse them.

### View all error events
```bash
python scripts/generate_ai_insights.py ... 2>&1 | jq 'select(.level=="ERROR")'
```

### Trace a specific Run ID
```bash
grep "run_12345" application.log | jq '.'
```

### Common Events
- `ingest_run_start` / `ingest_run_completed`
- `ai_generation_start` / `ai_generation_success` / `ai_generation_failed`
- `metrics_validation_failed`

## 2. CI/CD Operations
The pipeline runs automatically on GitHub Actions.
- **Validation Job**: Runs `flake8` and `pytest`.
- **Smoke Job**: Runs a full miniature pipeline (Simulation -> DB -> AI Mock).

**To run the smoke test locally:**
```bash
make smoke
```

## 3. Troubleshooting Guide

### Issue: "Run directory not found" in API
- **Cause**: The run `run_id` exists in DB but artifacts are missing on disk.
- **Fix**: Re-download artifacts from Azure/Backup or re-run simulation.
  ```bash
  python simulations/sweep.py ...
  ```

### Issue: "Validation Failed: Physics error"
- **Cause**: Simulation produced unstable results (e.g., $T_{max}$ exploded).
- **Fix**: This is working as intended. The system rejects bad data. Investigate parameters (e.g., reduce `dt`).

### Issue: AI Generation Failed
- **Check**: Is `AZURE_OPENAI_API_KEY` set?
- **Debug**: Run in mock mode to verify logic:
  ```bash
  python scripts/generate_ai_insights.py --run-dir results/runs/abc --mock
  ```

## 4. Replay Procedures
To re-process a specific run (e.g., after fixing a bug in metrics extraction):

1.  **Re-extract Metrics**:
    ```bash
    python scripts/extract_metrics.py --run-dir results/runs/<id>
    ```
2.  **Re-ingest to DB**:
    ```bash
    python scripts/ingest_data.py --runs-dir results/runs --overwrite
    ```
3.  **Re-generate Insights**:
    ```bash
    python scripts/generate_ai_insights.py --run-dir results/runs/<id>
    ```
