import pytest
import json
import os
import shutil
from pathlib import Path
from scripts.extract_metrics import extract_run_metrics
from scripts.validate_metrics import validate_run_metrics, load_schema
import jsonschema

# Fixture to create a dummy run
@pytest.fixture
def dummy_run(tmp_path):
    run_dir = tmp_path / "run_dummy"
    run_dir.mkdir()
    
    metadata = {
        "run_id": "run_dummy",
        "alpha": 0.1,
        "nx": 50,
        "dt": 0.001,
        "L": 1.0,
        "t_max": 0.5,
        "steps": 500,
        "duration_ms": 1200,
        "platform": "Linux",
        "created_at": "2025-01-01T12:00:00"
    }
    
    metrics = {
        "max_temperature": 0.8,
        "min_temperature": 0.0,
        "mean_temperature": 0.2,
        "energy_like_metric": 0.05,
        "stability_ratio": 0.04
    }
    
    with open(run_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)
        
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f)
        
    return str(run_dir)

def test_schema_validity():
    """Ensure the schema itself is valid JSON Schema."""
    schema = load_schema()
    # jsonschema.validate raises if schema is invalid, but checking specifically for schema definition
    jsonschema.Draft7Validator.check_schema(schema)

def test_extract_valid_run(dummy_run):
    """Test full extraction from a valid run."""
    payload = extract_run_metrics(dummy_run)
    
    assert payload["run_id"] == "run_dummy"
    assert payload["parameter_set"]["alpha"] == 0.1
    assert payload["performance_metrics"]["max_temperature"] == 0.8
    assert payload["quality_metrics"]["converged"] == True
    
    # Check schema compliance
    is_valid, errors = validate_run_metrics(payload)
    assert is_valid, f"Validation failed: {errors}"

def test_validation_physics_error():
    """Test validation catches physics errors (max < min)."""
    payload = {
        "run_id": "test_fail",
        "parameter_set": {"alpha": 1, "nx": 10},
        "performance_metrics": {
            "max_temperature": 0.1,
            "min_temperature": 0.5, # FAIL: min > max
            "mean_temperature": 0.3,
            "stability_ratio": 0.1
        },
        "quality_metrics": {"converged": True, "steps": 10},
        "execution_metrics": {"timestamp": "2025-01-01T00:00:00", "platform": "test"}
    }
    
    is_valid, errors = validate_run_metrics(payload)
    assert not is_valid
    assert any("max_temp" in e for e in errors)

def test_validation_stability_error():
    """Test validation catches stability warnings."""
    payload = {
        "run_id": "test_unstable",
        "parameter_set": {"alpha": 1, "nx": 10},
        "performance_metrics": {
            "max_temperature": 100,
            "min_temperature": 0,
            "mean_temperature": 50,
            "stability_ratio": 0.6  # FAIL: > 0.5
        },
        "quality_metrics": {"converged": True, "steps": 10},
        "execution_metrics": {"timestamp": "2025-01-01T00:00:00", "platform": "test"}
    }
    
    is_valid, errors = validate_run_metrics(payload)
    assert not is_valid
    assert any("stability_ratio" in e for e in errors)
