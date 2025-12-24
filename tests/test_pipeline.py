import pytest
import os
import sys
import json

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulations.sweep import run_simulation

def test_pipeline_small_sweep(tmp_path):
    """
    Integration Test: Run a minimal sweep and verify file generation.
    Uses pytest's tmp_path fixture to avoid polluting the actual results dir.
    """
    # 1. Setup
    runs_dir = tmp_path / "runs"
    # Ensure it exists (sweep logic normally does, but let's be safe)
    runs_dir.mkdir()
    
    params = {
        'L': 1.0,
        'nx': 10,
        'alpha': 0.1,
        't_max': 0.01,
        'dt': None,
        'save_interval': 5
    }
    
    # 2. Execute
    # We pass the Path object converted to string as output_base_dir
    run_output_path = run_simulation(params, str(runs_dir))
    
    # Refactor Note: run_simulation now returns the path string on success, not True
    assert run_output_path is not None, "run_simulation should return output path on success"
    assert os.path.exists(run_output_path), "Output directory should exist"
    
    # 3. Verify Artifacts
    # Find the created run directory (should be run_<hash>)
    generated_runs = list(runs_dir.iterdir())
    assert len(generated_runs) == 1, "Should have created exactly one run folder"
    
    run_dir = generated_runs[0]
    
    # Check essential files
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "timeseries.csv").exists()
    
    # Optional: content check
    with open(run_dir / "metrics.json") as f:
        metrics = json.load(f)
        assert "energy_like_metric" in metrics
        assert "stability_ratio" in metrics
