import sys
import os
import itertools
import yaml
import csv
import hashlib
import json
import numpy as np
import subprocess
import platform
import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from simulations.solver import HeatEquationSolver1D
# Import new metrics library
from analysis.metrics import compute_run_metrics, load_timeseries
# Import cloud storage
from scripts.cloud_storage import AzureRunStorage

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_git_revision_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return None

def get_stable_id(params):
    """Generate a stable ID based on parameter values."""
    # Ensure standard types for hashing
    clean_params = params.copy()
    param_str = json.dumps(clean_params, sort_keys=True)
    return hashlib.md5(param_str.encode('utf-8')).hexdigest()[:8]

def run_simulation(params, output_base_dir):
    """
    Run a single simulation with given params and save results.
    """
    run_id = f"run_{get_stable_id(params)}"
    print(f"Starting run {run_id} with params: {params}")
    
    L = params.get('L', 1.0)
    nx = int(params.get('nx', 50))
    alpha = params.get('alpha', 0.1)
    t_max = params.get('t_max', 0.5)
    dt = params.get('dt', None)
    save_interval = int(params.get('save_interval', 20))
    
    try:
        solver = HeatEquationSolver1D(L=L, nx=nx, alpha=alpha, t_max=t_max, dt=dt)
        
        # Consistent initial condition for fair comparison
        # Peak in center
        def initial_peak(x):
            return np.exp(-100 * (x - 0.5)**2)
        
        solver.set_initial_condition(initial_peak)
        
        results = solver.solve(save_interval=save_interval)
        
        # Save results (FileSystem)
        run_dir = os.path.join(output_base_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)
        
        # 1. Save results CSV
        data = []
        for t, u in results:
            row = {'time': t}
            for i, val in enumerate(u):
                row[f'p{i}'] = val
            data.append(row)
            
        csv_path = os.path.join(run_dir, "timeseries.csv")
        
        if pd:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
        else:
            if data:
                fieldnames = list(data[0].keys())
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                    
        # 2. Enrich and Save Metadata
        run_metadata = params.copy()
        
        # Enriched fields
        run_metadata['actual_dt'] = solver.dt
        run_metadata['steps'] = solver.nt
        run_metadata['run_id'] = run_id
        run_metadata['git_commit_hash'] = get_git_revision_hash()
        run_metadata['python_version'] = platform.python_version()
        run_metadata['platform'] = platform.system()
        run_metadata['created_at'] = datetime.datetime.utcnow().isoformat()
        
        with open(os.path.join(run_dir, "metadata.json"), 'w') as f:
            json.dump(run_metadata, f, indent=2)
            
        # 3. Compute Metrics (Strictly from CSV/Saved State)
        # We rely on the analysis library to compute metrics
        # Load back the data we just saved (or use in-memory df equivalent if we trust it matches)
        # For strict compliance "metrics must be computed from timeseries.csv", we'll reload.
        
        if pd:
            loaded_df = load_timeseries(csv_path)
            metrics = compute_run_metrics(loaded_df, solver.dx, solver.dt, alpha)
            
            with open(os.path.join(run_dir, "metrics.json"), 'w') as f:
                json.dump(metrics, f, indent=2)
                
        else:
            # Fallback if no pandas (simpler inline or skip)
            # requirement says "Use clear, testable code". 
            # If no pandas, we might skip or read csv manually. 
            # Given we installed pandas in requirements, we assume it's there.
            print("Warning: Pandas not found, skipping metrics generation.")

        print(f"  -> Run {run_id} completed. Saved to {run_dir}")
        return run_dir
        
    except Exception as e:
        print(f"  -> Run {run_id} FAILED: {e}")
        return None

def main():
    base_config_path = os.path.join(project_root, 'configs', 'base.yaml')
    
    # Allow overriding sweep config via env var
    sweep_config_env = os.environ.get("SWEEP_CONFIG")
    if sweep_config_env:
        sweep_config_path = os.path.abspath(sweep_config_env)
        print(f"Using sweep config from env: {sweep_config_path}")
    else:
        sweep_config_path = os.path.join(project_root, 'configs', 'sweep.yaml')
        print(f"Using default sweep config: {sweep_config_path}")
    
    base_config = load_config(base_config_path)
    sweep_config = load_config(sweep_config_path)
    
    base_params = base_config['simulation']
    sweep_params = sweep_config['sweep']
    
    # Generate Cartesian product of sweep parameters
    keys = list(sweep_params.keys())
    values = list(sweep_params.values())
    combinations = list(itertools.product(*values))
    
    print(f"Found {len(combinations)} parameter combinations to sweep.")
    
    # Allow overriding output root via env var
    output_root_env = os.environ.get("OUTPUT_ROOT")
    if output_root_env:
        results_dir = os.path.abspath(output_root_env)
        print(f"Using output root from env: {results_dir}")
    else:
        results_dir = os.path.join(project_root, 'results', 'runs')
        print(f"Using default output root: {results_dir}")
        
    os.makedirs(results_dir, exist_ok=True)
    
    for combo in combinations:
        # Merge base params with sweep overrides
        current_params = base_params.copy()
        for i, key in enumerate(keys):
            current_params[key] = combo[i]
            
        # Run simulation
        run_dir = run_simulation(current_params, results_dir)
        
        # Attempt upload if successful
        if run_dir:
            # Initialize storage (will log warning if disabled)
            storage = AzureRunStorage()
            if storage.is_enabled():
                run_id = os.path.basename(run_dir)
                storage.upload_run(run_id, run_dir)

if __name__ == "__main__":
    main()
