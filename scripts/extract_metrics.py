import json
import os
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

def extract_run_metrics(run_dir):
    """
    Extracts metrics from a run directory and formats them according to the canonical schema.
    Returns: dict matching metrics_schema.json
    """
    run_path = Path(run_dir)
    metadata_path = run_path / "metadata.json"
    metrics_path = run_path / "metrics.json"

    if not metadata_path.exists() or not metrics_path.exists():
        raise FileNotFoundError(f"Missing artifacts in {run_dir}")

    with open(metadata_path, 'r') as f:
        meta = json.load(f)
    
    with open(metrics_path, 'r') as f:
        raw_metrics = json.load(f)

    # 1. Parameter Set
    # Extract explicitly known parameters to avoid polluting with systems metadata
    parameter_set = {
        "alpha": float(meta.get("alpha", 0)),
        "nx": int(meta.get("nx", 0)),
        "dt": float(meta.get("dt")) if meta.get("dt") is not None else float(meta.get("actual_dt", 0)),
        "L": float(meta.get("L", 1.0)),
        "t_max": float(meta.get("t_max", 0.5))
    }

    # 2. Performance Metrics
    performance_metrics = {
        "max_temperature": float(raw_metrics.get("max_temperature", 0.0)),
        "min_temperature": float(raw_metrics.get("min_temperature", 0.0)),
        "mean_temperature": float(raw_metrics.get("mean_temperature", 0.0)),
        "energy_like_metric": float(raw_metrics.get("energy_like_metric", 0.0)),
        "stability_ratio": float(raw_metrics.get("stability_ratio", 0.0))
    }

    # 3. Quality Metrics
    # In this solver, currently we assume convergence if it finished. 
    # Real logic would check residuals. Here we check stability.
    is_stable = performance_metrics["stability_ratio"] <= 0.5
    
    # Calculate dx from L and nx if available
    L = parameter_set["L"]
    nx = parameter_set["nx"]
    dx = L / (nx - 1) if nx > 1 else 0.0

    quality_metrics = {
        "converged": is_stable, # Simplified proxy for this demo
        "steps": int(meta.get("steps", 0)),
        "dx": float(dx)
    }

    # 4. Execution Metrics
    execution_metrics = {
        "timestamp": meta.get("created_at", datetime.utcnow().isoformat()),
        "runtime_ms": float(meta.get("duration_ms", 0.0)), # Assuming 0 if not tracked
        "platform": meta.get("platform", "unknown"),
        "git_commit": meta.get("git_commit_hash")
    }

    # Assemble Payload
    canonical_payload = {
        "run_id": meta.get("run_id", run_path.name),
        "parameter_set": parameter_set,
        "performance_metrics": performance_metrics,
        "quality_metrics": quality_metrics,
        "execution_metrics": execution_metrics
    }

    return canonical_payload

def main():
    parser = argparse.ArgumentParser(description="Extract canonical metrics from run artifacts.")
    parser.add_argument("--run-dir", type=str, required=True, help="Path to simulation run directory")
    parser.add_argument("--output", type=str, help="Path to save canonical metrics.json", default=None)
    
    args = parser.parse_args()
    
    try:
        payload = extract_run_metrics(args.run_dir)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(payload, f, indent=2)
            print(f"Metrics saved to {args.output}")
        else:
            print(json.dumps(payload, indent=2))
            
    except Exception as e:
        print(f"Error extracting metrics: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
