import json
import os
import sys
import argparse
import jsonschema
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

SCHEMA_PATH = os.path.join(project_root, 'metrics', 'metrics_schema.json')

def load_schema():
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

def validate_run_metrics(metrics_payload):
    """
    Validates a metrics object against the schema and domain rules.
    Returns: (bool, list_of_errors)
    """
    errors = []
    
    # 1. Structural Schema Validation
    try:
        schema = load_schema()
        jsonschema.validate(instance=metrics_payload, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema Violation: {e.message}")
        # Stop early if schema fails widely
        return False, errors

    # 2. Domain Logic / Physics Checks
    perf = metrics_payload.get("performance_metrics", {})
    quality = metrics_payload.get("quality_metrics", {})
    params = metrics_payload.get("parameter_set", {})

    # Rule: Max Temp should not be less than Min Temp
    if perf.get("max_temperature") < perf.get("min_temperature"):
        errors.append(f"Physics Error: max_temp ({perf.get('max_temperature')}) < min_temp ({perf.get('min_temperature')})")

    # Rule: Stability Logic
    # If stability_ratio > 0.5, theoretical stability is lost.
    # We might expect 'converged' to be false, or at least flag it.
    stability_ratio = perf.get("stability_ratio", 0)
    is_converged = quality.get("converged", True)
    
    if stability_ratio > 0.5 and is_converged:
        # This is a soft warning or hard failure depending on strictness. 
        # For this pipeline, we flag it as an inconsistency.
        errors.append(f"Logic Error: Run marked converged but stability_ratio {stability_ratio:.4f} > 0.5")

    # Rule: Non-negative Time/Steps
    if quality.get("steps", -1) < 0:
        errors.append("Invalid State: steps cannot be negative")
        
    # Rule: Energy should be non-negative (for this specific heat equation setup with u^2)
    if perf.get("energy_like_metric", -1) < 0:
        errors.append("Physics Error: energy_like_metric cannot be negative")

    return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(description="Validate canonical metrics payload.")
    parser.add_argument("--metrics-file", type=str, required=True, help="Path to canonical metrics.json")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.metrics_file):
        print(f"File not found: {args.metrics_file}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.metrics_file, 'r') as f:
        payload = json.load(f)
        
    is_valid, errors = validate_run_metrics(payload)
    
    if is_valid:
        print("PASS: Metrics are valid.")
        sys.exit(0)
    else:
        print("FAIL: Validation errors found:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
