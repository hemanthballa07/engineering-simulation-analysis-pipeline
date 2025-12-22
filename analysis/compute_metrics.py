import os
import sys
import glob
import json
import pandas as pd

# Add project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from analysis.metrics import compute_run_metrics, load_timeseries

def process_all_runs(results_dir):
    """Scan results directory and regenerate metrics.json for all runs."""
    run_dirs = glob.glob(os.path.join(results_dir, 'run_*'))
    print(f"Found {len(run_dirs)} runs in {results_dir}")
    
    for r_dir in run_dirs:
        if not os.path.isdir(r_dir):
            continue
            
        csv_path = os.path.join(r_dir, 'timeseries.csv')
        meta_path = os.path.join(r_dir, 'metadata.json')
        metrics_path = os.path.join(r_dir, 'metrics.json')
        
        if not os.path.exists(csv_path) or not os.path.exists(meta_path):
            print(f"Skipping {os.path.basename(r_dir)}: missing csv or metadata")
            continue
            
        try:
            # Load Data
            df = load_timeseries(csv_path)
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            
            # Extract Physics Params
            # Use 'actual_dt' if available (computed), else 'dt' from params
            dt = meta.get('actual_dt', meta.get('dt'))
            if dt is None: 
                print(f"Warning: No dt found for {os.path.basename(r_dir)}")
                continue
                
            L = meta.get('L', 1.0)
            nx = meta.get('nx', 50)
            dx = L / (nx - 1)
            alpha = meta.get('alpha', 0.1)
            
            # Compute Metrics
            metrics = compute_run_metrics(df, dx, dt, alpha)
            
            # Save
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
                
            print(f"Generated metrics for {os.path.basename(r_dir)}")
            
        except Exception as e:
            print(f"Failed to process {os.path.basename(r_dir)}: {e}")

if __name__ == "__main__":
    results_dir = os.path.join(project_root, 'results')
    process_all_runs(results_dir)
